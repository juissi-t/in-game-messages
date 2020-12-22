import pytest
from slack_sdk.web.client import WebClient
from slack_sdk.errors import SlackApiError
from in_game_messages.slack_messaging import SlackMessaging


@pytest.fixture
def sender():
    return {
        "name": "tom n (The Lizards)",
        "icons": {
            "league": "https://1",
            "player": None,
            "race": "https://2",
        },
    }


def test_send_slack_message(monkeypatch, sender):
    def mock_post_message(*args, **kwargs):
        return {"ts": "1"}

    monkeypatch.setattr(WebClient, "chat_postMessage", mock_post_message)
    slack_messaging = SlackMessaging("abcd", "#channel")
    result = slack_messaging.send_slack_message("Testing", sender, None)
    assert result["ts"] == "1"


def test_send_slack_message_with_parent(monkeypatch, sender):
    def mock_post_message(*args, **kwargs):
        return {"ts": "2"}

    def mock_get_permalink(*args, **kwargs):
        return {"permalink": "https://2"}

    monkeypatch.setattr(WebClient, "chat_postMessage", mock_post_message)
    monkeypatch.setattr(WebClient, "chat_getPermalink", mock_get_permalink)

    slack_messaging = SlackMessaging("abcd", "#channel")
    result = slack_messaging.send_slack_message("Testing", sender, "1")
    assert result["ts"] == "2"


def test_send_slack_message_error(monkeypatch, sender):
    def mock_post_message(*args, **kwargs):
        raise SlackApiError(message="Test exception", response=400)

    monkeypatch.setattr(WebClient, "chat_postMessage", mock_post_message)

    slack_messaging = SlackMessaging("abcd", "#channel")
    with pytest.raises(SlackApiError) as excinfo:
        slack_messaging.send_slack_message("Testing", sender, None)
    assert "Test exception" in str(excinfo.value)


def test_send_new_messages_to_slack():
    pass


def test_construct_slack_message(message_no_replies):
    recipients = {
        "coen1970 (The Colonies)": '"coen1970 (The Colonies)" <coen1970@374955.planets.nu>',
    }
    message_no_replies["recipients"] = recipients
    message = SlackMessaging.construct_slack_message(message_no_replies)
    assert isinstance(message, str)
    assert message.startswith(
        "*Turn 21*\n*To:* coen1970 (The Colonies)\n*Date*: 2020-07-06T04:17:23\n\nHi Coen,"
    )
