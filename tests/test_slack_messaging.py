import mailbox

import pytest
import requests
from in_game_messages.messaging import Messaging
from in_game_messages.slack_messaging import SlackMessaging
from slack_sdk.errors import SlackApiError
from slack_sdk.web.client import WebClient


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

    monkeypatch.setattr(WebClient, "chat_getPermalink", mock_get_permalink)
    monkeypatch.setattr(WebClient, "chat_postMessage", mock_post_message)

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


def test_send_new_messages_to_slack(monkeypatch, tmp_path, all_messages):
    class MockResponseMessages:
        @staticmethod
        def json():
            return all_messages

    def mock_post(*args, **kwargs):
        return MockResponseMessages()

    def mock_get_permalink(*args, **kwargs):
        return {"permalink": "https://2"}

    def mock_post_message(*args, **kwargs):
        return {"ts": "2"}

    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(WebClient, "chat_getPermalink", mock_get_permalink)
    monkeypatch.setattr(WebClient, "chat_postMessage", mock_post_message)

    mbox_path = tmp_path / "mbox"
    messaging = Messaging("abcd")
    messages = messaging.get_messages_from_game("374955", "1")
    slack_messaging = SlackMessaging("abcd", "#channel")
    slack_messaging.send_new_messages_to_slack(messages, "374955", mbox_path)
    # We don't have a good way to see the messages were posted successfully other
    # than checking they exist in the mailbox afterwards
    mailbox_mbox = mailbox.mbox(mbox_path)
    assert mailbox_mbox.__len__() == 3


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
