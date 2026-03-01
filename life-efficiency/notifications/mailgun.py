import logging
import os
from typing import Iterable

logger = logging.getLogger(__name__)


def _split_emails(value: str) -> list[str]:
    parts = [p.strip() for p in value.split(",")]
    return [p for p in parts if p]


def send_email_via_mailgun(
    *,
    subject: str,
    text: str,
    to_emails: Iterable[str],
    domain: str,
    api_key: str,
    from_email: str,
    timeout_seconds: int = 15,
) -> dict:
    import requests

    url = f"https://api.mailgun.net/v3/{domain}/messages"
    to_list = list(to_emails)
    res = requests.post(
        url,
        auth=("api", api_key),
        data={
            "from": from_email,
            "to": to_list,
            "subject": subject,
            "text": text,
        },
        timeout=timeout_seconds,
    )
    return {"status_code": res.status_code, "text": res.text}


def send_stale_reply_alert_if_configured(
    *,
    chat_username: str,
    threshold_hours: float,
    stats: dict,
) -> dict:
    api_key = os.environ.get("MAILGUN_API_KEY", "").strip()
    domain = os.environ.get("MAILGUN_DOMAIN", "").strip()
    from_email = os.environ.get("MAILGUN_FROM", "").strip()
    to_raw = os.environ.get(
        "MAILGUN_TO",
        "leon.patmore@gmail.com,leon.patmore@gendigital.com",
    ).strip()

    if not api_key or not domain:
        logger.info("Mailgun not configured (need MAILGUN_API_KEY and MAILGUN_DOMAIN); skipping email")
        return {"sent": False, "reason": "mailgun not configured"}

    if not from_email:
        from_email = f"Life Efficiency <postmaster@{domain}>"

    to_emails = _split_emails(to_raw)
    if not to_emails:
        logger.info("MAILGUN_TO is empty; skipping email")
        return {"sent": False, "reason": "no recipients"}

    subject = f"Telegram reply stale: {chat_username}"
    text = (
        f"Telegram chat: {chat_username}\n"
        f"Threshold hours: {threshold_hours}\n"
        f"Checked at: {stats.get('checked_at')}\n"
        f"Last incoming at: {stats.get('last_incoming_at')}\n"
        f"Last incoming age hours: {stats.get('last_incoming_age_hours')}\n"
        f"Last outgoing at: {stats.get('last_outgoing_at')}\n"
        f"Last outgoing age hours: {stats.get('last_outgoing_age_hours')}\n"
    )

    try:
        result = send_email_via_mailgun(
            subject=subject,
            text=text,
            to_emails=to_emails,
            domain=domain,
            api_key=api_key,
            from_email=from_email,
        )
        ok = 200 <= int(result["status_code"]) < 300
        if ok:
            logger.warning("Mailgun alert email sent for chat %s", chat_username)
            return {"sent": True, "mailgun": result}
        logger.error("Mailgun alert email failed for chat %s: %s", chat_username, result)
        return {"sent": False, "reason": "mailgun error", "mailgun": result}
    except Exception as e:
        logger.exception("Mailgun alert email exception: %s", e)
        return {"sent": False, "reason": str(e)}

