import json
import logging
import os
import time
import urllib.error
import urllib.request

from telegram.checker import check_reply_age
from notifications.mailgun import send_stale_reply_alert_if_configured

logger = logging.getLogger(__name__)
_log_level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
_log_level = getattr(logging, _log_level_name, logging.INFO)
logging.getLogger().setLevel(_log_level)
logger.setLevel(_log_level)

EXTENSION_PORT = os.environ.get("PARAMETERS_SECRETS_EXTENSION_HTTP_PORT", "2773")


def _get_secret_json(secret_id: str) -> dict:
    timeout_seconds = float(os.environ.get("SECRETS_FETCH_TIMEOUT_SECONDS", "5"))
    logger.info("Fetching secret [%s] with timeout %.1fs", secret_id, timeout_seconds)
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
    if endpoint_url:
        import boto3
        from botocore.config import Config

        client = boto3.client(
            "secretsmanager",
            endpoint_url=endpoint_url,
            config=Config(
                connect_timeout=timeout_seconds,
                read_timeout=timeout_seconds,
                retries={"max_attempts": 1},
            ),
        )
        response = client.get_secret_value(SecretId=secret_id)
        return json.loads(response["SecretString"])

    url = f"http://localhost:{EXTENSION_PORT}/secretsmanager/get?secretId={secret_id}"
    req = urllib.request.Request(url, headers={"X-Aws-Parameters-Secrets-Token": os.environ["AWS_SESSION_TOKEN"]})
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        data = json.loads(resp.read().decode())
    return json.loads(data["SecretString"])


def _load_env_from_secret(secret_id: str) -> dict | None:
    try:
        secret_values = _get_secret_json(secret_id)
    except (KeyError, ValueError, TypeError) as e:
        logger.error("Invalid Telegram secret (expect JSON object with env key/value pairs): %s", e)
        return {"status": "error", "reason": "invalid Telegram secret"}
    except Exception as e:
        logger.error("Failed to get Telegram secret: %s", e)
        return {"status": "error", "reason": "secret unavailable"}

    if not isinstance(secret_values, dict):
        logger.error("Invalid Telegram secret: expected JSON object of env key/value pairs")
        return {"status": "error", "reason": "invalid Telegram secret"}

    for key, value in secret_values.items():
        if not isinstance(key, str):
            logger.error("Invalid Telegram secret key type: expected string keys")
            return {"status": "error", "reason": "invalid Telegram secret"}
        if value is None:
            continue
        os.environ[key] = str(value)

    return None


def _parse_threshold_hours(threshold_str: str) -> float:
    try:
        return float(threshold_str)
    except ValueError:
        logger.warning("Invalid REPLY_ALERT_THRESHOLD_HOURS %s; using 2.5", threshold_str)
        return 2.5


def _should_send_email_alert(*, stats: dict, threshold_hours: float) -> tuple[bool, str]:
    if not stats.get("alerted"):
        return False, "skip email: checker did not alert"
    if not stats.get("needs_reply", False):
        return False, "skip email: needs_reply is false"
    if stats.get("latest_message_out") is True:
        return False, "skip email: latest message is outgoing"
    age = stats.get("unreplied_age_hours", stats.get("last_incoming_age_hours"))
    if age is None:
        return False, "skip email: no unreplied/last incoming age available"

    age_hours = float(age)
    should_send = age_hours >= threshold_hours
    if should_send:
        return (
            True,
            f"send email: age_hours={age_hours:.2f} is >= threshold_hours={threshold_hours:.2f}",
        )
    return (
        False,
        f"skip email: age_hours={age_hours:.2f} is below threshold_hours={threshold_hours:.2f}",
    )


def _parse_api_id(api_id_str: str) -> int | dict:
    try:
        return int(api_id_str)
    except ValueError:
        logger.error("TELEGRAM_API_ID must be an integer; got %s", api_id_str)
        return {"status": "error", "reason": "invalid TELEGRAM_API_ID"}


def handler(event, context):
    start = time.perf_counter()
    request_id = getattr(context, "aws_request_id", "unknown")
    logger.info("Telegram handler start request_id=%s", request_id)

    secret_arn = os.environ.get("TELEGRAM_SECRET_ARN", "").strip()

    if secret_arn:
        secret_start = time.perf_counter()
        load_error = _load_env_from_secret(secret_arn)
        logger.info("Secret load finished in %.1fms", (time.perf_counter() - secret_start) * 1000)
        if load_error:
            return load_error

    api_id_str = os.environ.get("TELEGRAM_API_ID", "").strip()
    api_hash_env = os.environ.get("TELEGRAM_API_HASH", "").strip()
    session_string = os.environ.get("TELEGRAM_SESSION_STRING")
    target_chat_username = os.environ.get("TARGET_CHAT_USERNAME")
    threshold_str = os.environ.get("REPLY_ALERT_THRESHOLD_HOURS", "2.5")

    if not target_chat_username:
        logger.error("Missing required env var TARGET_CHAT_USERNAME; skipping Telegram reply check")
        return {"status": "skipped", "reason": "missing env: TARGET_CHAT_USERNAME"}

    if not api_id_str or not api_hash_env:
        logger.error("Missing credentials: set TELEGRAM_API_ID and TELEGRAM_API_HASH")
        return {"status": "skipped", "reason": "missing env: TELEGRAM_API_ID/TELEGRAM_API_HASH"}

    parsed_api_id = _parse_api_id(api_id_str)
    if isinstance(parsed_api_id, dict):
        return parsed_api_id
    api_id = parsed_api_id
    api_hash = api_hash_env

    if not session_string:
        logger.error("Missing required TELEGRAM_SESSION_STRING; skipping Telegram reply check")
        return {"status": "skipped", "reason": "missing env: TELEGRAM_SESSION_STRING"}

    threshold_hours = _parse_threshold_hours(threshold_str)

    try:
        checker_start = time.perf_counter()
        logger.info("Running Telegram checker for chat [%s]", target_chat_username.strip())
        stats = check_reply_age(
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string,
            target_chat_username=target_chat_username.strip(),
            max_age_hours=threshold_hours,
        )
        logger.info("Telegram checker finished in %.1fms", (time.perf_counter() - checker_start) * 1000)
        if not isinstance(stats, dict):
            stats = {"alerted": False}
        email = None
        should_send_email, email_decision = _should_send_email_alert(stats=stats, threshold_hours=threshold_hours)
        if should_send_email:
            email_start = time.perf_counter()
            logger.info("Threshold crossed, sending Mailgun alert (%s)", email_decision)
            email = send_stale_reply_alert_if_configured(
                chat_username=target_chat_username.strip(),
                threshold_hours=threshold_hours,
                stats=stats,
            )
            logger.info("Mailgun alert step finished in %.1fms", (time.perf_counter() - email_start) * 1000)
        else:
            logger.info("Mailgun alert not sent (%s)", email_decision)
        logger.info("Telegram handler completed in %.1fms", (time.perf_counter() - start) * 1000)
        return {"status": "ok", "stats": stats, "email": email}
    except Exception as e:
        logger.exception("Telegram reply check failed: %s", e)
        return {"status": "error", "reason": str(e)}
