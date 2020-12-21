import pytest

from in_game_messages.slack_messaging import SlackMessaging


def test_send_slack_message():
    pass


def test_send_new_messages_to_slack():
    pass


def test_save_email_message():
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
