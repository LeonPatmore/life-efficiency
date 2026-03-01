import asyncio
import faulthandler
import logging
import socket
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

REPLY_ALERT_THRESHOLD_HOURS = 2.0
STATS_MESSAGE_LIMIT = 30
TELEGRAM_CONNECT_TIMEOUT_SECONDS = 12.0


def _normalize_username(username: str) -> str:
    return username.lstrip("@")


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _probe_tcp(host: str, port: int, timeout_seconds: float) -> None:
    probe_start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            pass
        logger.info(
            "TCP probe to %s:%s succeeded in %.1fms",
            host,
            port,
            (time.perf_counter() - probe_start) * 1000,
        )
    except Exception as e:
        logger.error(
            "TCP probe to %s:%s failed after %.1fms: %s",
            host,
            port,
            (time.perf_counter() - probe_start) * 1000,
            e,
        )


async def check_reply_age_async(
    api_id: int,
    api_hash: str,
    session_string: str,
    target_chat_username: str,
    max_age_hours: float = REPLY_ALERT_THRESHOLD_HOURS,
) -> dict:
    start = time.perf_counter()
    logger.info("Telegram checker async start for chat [%s]", target_chat_username)

    _probe_tcp("api.telegram.org", 443, TELEGRAM_CONNECT_TIMEOUT_SECONDS)
    logger.info("Importing Telethon modules")
    faulthandler.dump_traceback_later(8, repeat=False)
    from telethon import TelegramClient
    logger.info("Imported TelegramClient")
    from telethon.sessions import StringSession
    faulthandler.cancel_dump_traceback_later()
    logger.info("Imported StringSession")

    client = TelegramClient(
        StringSession(session_string),
        api_id,
        api_hash,
        timeout=TELEGRAM_CONNECT_TIMEOUT_SECONDS,
        request_retries=1,
        connection_retries=0,
        auto_reconnect=False,
    )
    connect_start = time.perf_counter()
    try:
        await asyncio.wait_for(client.connect(), timeout=TELEGRAM_CONNECT_TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        logger.error("Telethon connect timed out after %.1fs", TELEGRAM_CONNECT_TIMEOUT_SECONDS)
        return {"status": "error", "reason": "telegram connect timeout"}
    logger.info("Telethon connect finished in %.1fms", (time.perf_counter() - connect_start) * 1000)
    if not await client.is_user_authorized():
        logger.warning("Telegram session not authorized; skipping reply check")
        return {"skipped": True, "reason": "unauthorized"}

    try:
        username = _normalize_username(target_chat_username)
        entity_start = time.perf_counter()
        entity = await client.get_entity(username)
        logger.info("Telegram get_entity finished in %.1fms", (time.perf_counter() - entity_start) * 1000)
        messages_start = time.perf_counter()
        messages = await client.get_messages(entity, limit=STATS_MESSAGE_LIMIT)
        logger.info("Telegram get_messages finished in %.1fms", (time.perf_counter() - messages_start) * 1000)
        latest_message_out = None
        if messages:
            latest_message_out = bool(getattr(messages[0], "out", False))
        latest_incoming = None
        latest_outgoing = None
        for msg in messages:
            if latest_outgoing is None and getattr(msg, "out", False):
                latest_outgoing = msg
            if latest_incoming is None and not getattr(msg, "out", True):
                latest_incoming = msg
            if latest_incoming is not None and latest_outgoing is not None:
                break

        now = datetime.now(timezone.utc)
        latest_incoming_time = _ensure_utc(latest_incoming.date) if latest_incoming else None
        latest_outgoing_time = _ensure_utc(latest_outgoing.date) if latest_outgoing else None
        incoming_times = [
            _ensure_utc(msg.date) for msg in messages if not getattr(msg, "out", True)
        ]

        latest_incoming_age_hours = (
            (now - latest_incoming_time).total_seconds() / 3600.0 if latest_incoming_time else None
        )
        latest_outgoing_age_hours = (
            (now - latest_outgoing_time).total_seconds() / 3600.0 if latest_outgoing_time else None
        )

        first_unreplied_incoming_time = None
        if incoming_times:
            if latest_outgoing_time is None:
                first_unreplied_incoming_time = min(incoming_times)
            else:
                unreplied_candidates = [dt for dt in incoming_times if dt > latest_outgoing_time]
                if unreplied_candidates:
                    first_unreplied_incoming_time = min(unreplied_candidates)

        needs_reply = first_unreplied_incoming_time is not None
        unreplied_age_hours = (
            (now - first_unreplied_incoming_time).total_seconds() / 3600.0
            if first_unreplied_incoming_time
            else None
        )

        logger.info(
            "Telegram stats for [%s]: last_incoming_at=%s last_incoming_age_hours=%s "
            "last_outgoing_at=%s last_outgoing_age_hours=%s first_unreplied_incoming_at=%s "
            "unreplied_age_hours=%s latest_message_out=%s needs_reply=%s "
            "(checked_at=%s, threshold_hours=%.1f)",
            target_chat_username,
            latest_incoming_time.isoformat() if latest_incoming_time else None,
            round(latest_incoming_age_hours, 2) if latest_incoming_age_hours is not None else None,
            latest_outgoing_time.isoformat() if latest_outgoing_time else None,
            round(latest_outgoing_age_hours, 2) if latest_outgoing_age_hours is not None else None,
            first_unreplied_incoming_time.isoformat() if first_unreplied_incoming_time else None,
            round(unreplied_age_hours, 2) if unreplied_age_hours is not None else None,
            latest_message_out,
            needs_reply,
            now.isoformat(),
            max_age_hours,
        )

        alerted = False
        if not needs_reply:
            logger.info(
                "No pending reply in chat [%s] (latest message is outgoing or no newer incoming message).",
                target_chat_username,
            )
        elif unreplied_age_hours is not None and unreplied_age_hours >= max_age_hours:
            alerted = True
            logger.warning(
                "ALERT: You have not replied in chat [%s] for %.1f hours since first unreplied incoming (at %s). "
                "Threshold: %.1f hours.",
                target_chat_username,
                unreplied_age_hours,
                first_unreplied_incoming_time.isoformat() if first_unreplied_incoming_time else None,
                max_age_hours,
            )
        else:
            logger.info(
                "Oldest unreplied message in chat [%s] is %.1f hours old; within threshold.",
                target_chat_username,
                unreplied_age_hours,
            )

        return {
            "alerted": alerted,
            "needs_reply": needs_reply,
            "latest_message_out": latest_message_out,
            "checked_at": now.isoformat(),
            "last_incoming_at": latest_incoming_time.isoformat() if latest_incoming_time else None,
            "last_incoming_age_hours": latest_incoming_age_hours,
            "last_outgoing_at": latest_outgoing_time.isoformat() if latest_outgoing_time else None,
            "last_outgoing_age_hours": latest_outgoing_age_hours,
            "first_unreplied_incoming_at": (
                first_unreplied_incoming_time.isoformat() if first_unreplied_incoming_time else None
            ),
            "unreplied_age_hours": unreplied_age_hours,
        }
    finally:
        disconnect_start = time.perf_counter()
        await client.disconnect()
        logger.info(
            "Telethon disconnect finished in %.1fms (checker total %.1fms)",
            (time.perf_counter() - disconnect_start) * 1000,
            (time.perf_counter() - start) * 1000,
        )


def check_reply_age(
    api_id: int,
    api_hash: str,
    session_string: str,
    target_chat_username: str,
    max_age_hours: float = REPLY_ALERT_THRESHOLD_HOURS,
) -> dict:
    return asyncio.run(
        check_reply_age_async(
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string,
            target_chat_username=target_chat_username,
            max_age_hours=max_age_hours,
        )
    )
