import os
from unittest.mock import patch

from telegram.handler import handler


def _env_with_secret_arn(extra=None):
    base = {
        "TELEGRAM_SECRET_ARN": "arn:aws:secretsmanager:eu-west-1:123:secret:telegram",
        "TELEGRAM_SESSION_STRING": "xyz",
        "TARGET_CHAT_USERNAME": "someone",
    }
    if extra:
        base.update(extra)
    return base


def test_handler_returns_skipped_when_env_missing():
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_SECRET_ARN": "",
            "TELEGRAM_SESSION_STRING": "",
            "TARGET_CHAT_USERNAME": "",
        },
    ):
        result = handler({}, None)
    assert result["status"] == "skipped"
    assert "missing" in result["reason"]


def test_handler_returns_error_when_secret_invalid():
    with patch.dict(os.environ, _env_with_secret_arn(), clear=True):
        with patch("telegram.handler._get_secret_json") as mock_get:
            mock_get.side_effect = ValueError("bad secret")
            result = handler({}, None)
    assert result["status"] == "error"
    assert "invalid Telegram secret" in result["reason"]


def test_handler_uses_default_threshold_when_invalid():
    with patch.dict(os.environ, _env_with_secret_arn(), clear=True):
        with patch("telegram.handler._get_secret_json", return_value={"TELEGRAM_API_ID": "12345", "TELEGRAM_API_HASH": "abc"}):
            with patch("telegram.handler.check_reply_age") as mock_check:
                mock_check.return_value = None
                result = handler({}, None)
    assert result["status"] == "ok"
    mock_check.assert_called_once()
    call_kw = mock_check.call_args[1]
    assert call_kw["max_age_hours"] == 3.0


def test_handler_sends_email_when_threshold_crossed():
    with patch.dict(
        os.environ,
        _env_with_secret_arn(
            {
                "REPLY_ALERT_THRESHOLD_HOURS": "3",
                "MAILGUN_ALERT_WINDOW_MINUTES": "20",
            }
        ),
        clear=True,
    ):
        with patch("telegram.handler._get_secret_json", return_value={"TELEGRAM_API_ID": "12345", "TELEGRAM_API_HASH": "abc"}):
            with patch(
                "telegram.handler.check_reply_age",
                return_value={
                    "alerted": True,
                    "needs_reply": True,
                    "latest_message_out": False,
                    "last_incoming_age_hours": 3.1,
                },
            ):
                with patch("telegram.handler.send_stale_reply_alert_if_configured") as mock_send:
                    mock_send.return_value = {"sent": True}
                    result = handler({}, None)
    assert result["status"] == "ok"
    assert result["email"] == {"sent": True}
    mock_send.assert_called_once()


def test_handler_does_not_send_email_outside_window():
    with patch.dict(
        os.environ,
        _env_with_secret_arn(
            {
                "REPLY_ALERT_THRESHOLD_HOURS": "3",
                "MAILGUN_ALERT_WINDOW_MINUTES": "20",
            }
        ),
        clear=True,
    ):
        with patch("telegram.handler._get_secret_json", return_value={"TELEGRAM_API_ID": "12345", "TELEGRAM_API_HASH": "abc"}):
            with patch(
                "telegram.handler.check_reply_age",
                return_value={
                    "alerted": True,
                    "needs_reply": True,
                    "latest_message_out": False,
                    "last_incoming_age_hours": 4.0,
                },
            ):
                with patch("telegram.handler.send_stale_reply_alert_if_configured") as mock_send:
                    result = handler({}, None)
    assert result["status"] == "ok"
    assert result["email"] is None
    mock_send.assert_not_called()


def test_handler_calls_checker_with_stripped_username():
    with patch.dict(
        os.environ,
        _env_with_secret_arn({"TARGET_CHAT_USERNAME": "  @someone  ", "REPLY_ALERT_THRESHOLD_HOURS": "3"}),
        clear=True,
    ):
        with patch("telegram.handler._get_secret_json", return_value={"TELEGRAM_API_ID": "12345", "TELEGRAM_API_HASH": "abc"}):
            with patch("telegram.handler.check_reply_age") as mock_check:
                mock_check.return_value = None
                result = handler({}, None)
    assert result["status"] == "ok"
    mock_check.assert_called_once()
    call_kw = mock_check.call_args[1]
    assert call_kw["target_chat_username"] == "@someone"
    assert call_kw["max_age_hours"] == 3.0


def test_handler_returns_error_on_check_exception():
    with patch.dict(os.environ, _env_with_secret_arn(), clear=True):
        with patch("telegram.handler._get_secret_json", return_value={"TELEGRAM_API_ID": "12345", "TELEGRAM_API_HASH": "abc"}):
            with patch("telegram.handler.check_reply_age") as mock_check:
                mock_check.side_effect = RuntimeError("connection failed")
                result = handler({}, None)
    assert result["status"] == "error"
    assert "connection failed" in result["reason"]


def test_handler_uses_env_credentials_when_no_secret_arn():
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_SECRET_ARN": "",
            "TELEGRAM_API_ID": "12345",
            "TELEGRAM_API_HASH": "abc",
            "TELEGRAM_SESSION_STRING": "xyz",
            "TARGET_CHAT_USERNAME": "someone",
        },
        clear=True,
    ):
        with patch("telegram.handler.check_reply_age") as mock_check:
            mock_check.return_value = None
            result = handler({}, None)
    assert result["status"] == "ok"
    mock_check.assert_called_once()
    call_kw = mock_check.call_args[1]
    assert call_kw["api_id"] == 12345
    assert call_kw["api_hash"] == "abc"


def test_handler_loads_envs_from_secret_before_checks():
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_SECRET_ARN": "arn:aws:secretsmanager:eu-west-1:123:secret:telegram",
            "TELEGRAM_SESSION_STRING": "",
            "TARGET_CHAT_USERNAME": "",
        },
        clear=True,
    ):
        with patch(
            "telegram.handler._get_secret_json",
            return_value={
                "TELEGRAM_API_ID": "12345",
                "TELEGRAM_API_HASH": "abc",
                "TELEGRAM_SESSION_STRING": "xyz",
                "TARGET_CHAT_USERNAME": "someone",
            },
        ):
            with patch("telegram.handler.check_reply_age") as mock_check:
                mock_check.return_value = None
                result = handler({}, None)
    assert result["status"] == "ok"
    mock_check.assert_called_once()


def test_handler_never_sends_email_when_latest_message_is_outgoing():
    with patch.dict(
        os.environ,
        _env_with_secret_arn(
            {
                "REPLY_ALERT_THRESHOLD_HOURS": "3",
                "MAILGUN_ALERT_WINDOW_MINUTES": "20",
            }
        ),
        clear=True,
    ):
        with patch("telegram.handler._get_secret_json", return_value={"TELEGRAM_API_ID": "12345", "TELEGRAM_API_HASH": "abc"}):
            with patch(
                "telegram.handler.check_reply_age",
                return_value={
                    "alerted": True,
                    "needs_reply": False,
                    "latest_message_out": True,
                    "last_incoming_age_hours": 10.0,
                },
            ):
                with patch("telegram.handler.send_stale_reply_alert_if_configured") as mock_send:
                    result = handler({}, None)
    assert result["status"] == "ok"
    assert result["email"] is None
    mock_send.assert_not_called()
