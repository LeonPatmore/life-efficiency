import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

REPLY_ALERT_THRESHOLD_HOURS = 2.0
STATS_MESSAGE_LIMIT = 30


def _normalize_username(username: str) -> str:
    return username.lstrip("@")


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


async def check_reply_age_async(
    api_id: int,
    api_hash: str,
    session_string: str,
    target_chat_username: str,
    max_age_hours: float = REPLY_ALERT_THRESHOLD_HOURS,
) -> dict:
    from telethon import TelegramClient
    from telethon.sessions import StringSession

    client = TelegramClient(
        StringSession(session_string),
        api_id,
        api_hash,
    )
    await client.connect()
    if not await client.is_user_authorized():
        logger.warning("Telegram session not authorized; skipping reply check")
        return {"skipped": True, "reason": "unauthorized"}

    try:
        username = _normalize_username(target_chat_username)
        entity = await client.get_entity(username)
        messages = await client.get_messages(entity, limit=STATS_MESSAGE_LIMIT)
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

        latest_incoming_age_hours = (
            (now - latest_incoming_time).total_seconds() / 3600.0 if latest_incoming_time else None
        )
        latest_outgoing_age_hours = (
            (now - latest_outgoing_time).total_seconds() / 3600.0 if latest_outgoing_time else None
        )

        needs_reply = False
        if latest_incoming_time is not None:
            needs_reply = latest_outgoing_time is None or latest_outgoing_time < latest_incoming_time

        logger.info(
            "Telegram stats for [%s]: last_incoming_at=%s last_incoming_age_hours=%s "
            "last_outgoing_at=%s last_outgoing_age_hours=%s latest_message_out=%s needs_reply=%s "
            "(checked_at=%s, threshold_hours=%.1f)",
            target_chat_username,
            latest_incoming_time.isoformat() if latest_incoming_time else None,
            round(latest_incoming_age_hours, 2) if latest_incoming_age_hours is not None else None,
            latest_outgoing_time.isoformat() if latest_outgoing_time else None,
            round(latest_outgoing_age_hours, 2) if latest_outgoing_age_hours is not None else None,
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
        elif latest_incoming_age_hours is not None and latest_incoming_age_hours >= max_age_hours:
            alerted = True
            logger.warning(
                "ALERT: You have not replied in chat [%s] for %.1f hours since last incoming (at %s). "
                "Threshold: %.1f hours.",
                target_chat_username,
                latest_incoming_age_hours,
                latest_incoming_time.isoformat(),
                max_age_hours,
            )
        else:
            logger.info(
                "Last reply in chat [%s] is %.1f hours old; within threshold.",
                target_chat_username,
                latest_incoming_age_hours,
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
        }
    finally:
        await client.disconnect()


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
