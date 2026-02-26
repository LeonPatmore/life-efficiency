import json
import logging
import os
import urllib.error
import urllib.request

from telegram.checker import check_reply_age
from notifications.mailgun import send_stale_reply_alert_if_configured

logger = logging.getLogger(__name__)

EXTENSION_PORT = os.environ.get("PARAMETERS_SECRETS_EXTENSION_HTTP_PORT", "2773")


def _get_secret_json(secret_id: str) -> dict:
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
    if endpoint_url:
        import boto3

        client = boto3.client("secretsmanager", endpoint_url=endpoint_url)
        response = client.get_secret_value(SecretId=secret_id)
        return json.loads(response["SecretString"])

    url = f"http://localhost:{EXTENSION_PORT}/secretsmanager/get?secretId={secret_id}"
    req = urllib.request.Request(url, headers={"X-Aws-Parameters-Secrets-Token": os.environ["AWS_SESSION_TOKEN"]})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    return json.loads(data["SecretString"])


def _parse_threshold_hours(threshold_str: str) -> float:
    try:
        return float(threshold_str)
    except ValueError:
        logger.warning("Invalid REPLY_ALERT_THRESHOLD_HOURS %s; using 3", threshold_str)
        return 3.0


def _should_send_email_alert(*, stats: dict, threshold_hours: float) -> bool:
    if not stats.get("alerted"):
        return False
    if not stats.get("needs_reply", False):
        return False
    if stats.get("latest_message_out") is True:
        return False
    age = stats.get("last_incoming_age_hours")
    if age is None:
        return False

    window_minutes = float(os.environ.get("MAILGUN_ALERT_WINDOW_MINUTES", "20"))
    window_hours = window_minutes / 60.0
    return threshold_hours <= float(age) < (threshold_hours + window_hours)


def _resolve_credentials(
    secret_id: str,
    api_id_str: str,
    api_hash_env: str,
    session_string: str | None,
) -> tuple[int, str, str | None] | dict:
    if secret_id:
        try:
            secret = _get_secret_json(secret_id)
            api_id = int(secret["api_id"])
            api_hash = secret["api_hash"]
            session_string = session_string or secret.get("session_string")
            return api_id, api_hash, session_string
        except (KeyError, ValueError, TypeError) as e:
            logger.error("Invalid Telegram secret (expect JSON with api_id and api_hash): %s", e)
            return {"status": "error", "reason": "invalid Telegram secret"}
        except Exception as e:
            logger.error("Failed to get Telegram secret: %s", e)
            return {"status": "error", "reason": "secret unavailable"}

    if api_id_str and api_hash_env:
        try:
            api_id = int(api_id_str)
        except ValueError:
            logger.error("TELEGRAM_API_ID must be an integer; got %s", api_id_str)
            return {"status": "error", "reason": "invalid TELEGRAM_API_ID"}
        return api_id, api_hash_env, session_string

    logger.error("Missing credentials: set TELEGRAM_SECRET_ARN or (TELEGRAM_API_ID and TELEGRAM_API_HASH)")
    return {"status": "skipped", "reason": "missing env: TELEGRAM_SECRET_ARN or TELEGRAM_API_ID/TELEGRAM_API_HASH"}


def handler(event, context):
    secret_arn = os.environ.get("TELEGRAM_SECRET_ARN", "").strip()
    api_id_str = os.environ.get("TELEGRAM_API_ID", "").strip()
    api_hash_env = os.environ.get("TELEGRAM_API_HASH", "").strip()
    session_string = os.environ.get("TELEGRAM_SESSION_STRING")
    target_chat_username = os.environ.get("TARGET_CHAT_USERNAME")
    threshold_str = os.environ.get("REPLY_ALERT_THRESHOLD_HOURS", "3")

    if not target_chat_username:
        logger.error("Missing required env var TARGET_CHAT_USERNAME; skipping Telegram reply check")
        return {"status": "skipped", "reason": "missing env: TARGET_CHAT_USERNAME"}

    resolved = _resolve_credentials(secret_arn, api_id_str, api_hash_env, session_string)
    if isinstance(resolved, dict):
        return resolved
    api_id, api_hash, session_string = resolved

    if not session_string:
        logger.error("Missing required TELEGRAM_SESSION_STRING (or session_string in secret); skipping Telegram reply check")
        return {"status": "skipped", "reason": "missing env: TELEGRAM_SESSION_STRING"}

    threshold_hours = _parse_threshold_hours(threshold_str)

    try:
        stats = check_reply_age(
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string,
            target_chat_username=target_chat_username.strip(),
            max_age_hours=threshold_hours,
        )
        if not isinstance(stats, dict):
            stats = {"alerted": False}
        email = None
        if _should_send_email_alert(stats=stats, threshold_hours=threshold_hours):
            email = send_stale_reply_alert_if_configured(
                chat_username=target_chat_username.strip(),
                threshold_hours=threshold_hours,
                stats=stats,
            )
        return {"status": "ok", "stats": stats, "email": email}
    except Exception as e:
        logger.exception("Telegram reply check failed: %s", e)
        return {"status": "error", "reason": str(e)}
