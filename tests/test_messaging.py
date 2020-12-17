import pytest

from in_game_messages.messaging import Messaging


def test_get_messages_from_game():
    pass


def test_get_all_messages_from_game():
    pass


def test_get_race_ids_for_game():
    pass


def test_get_message_participants():
    pass


def test_email_from_name():
    name = "foo (The Feds)"
    gameid = "1234"
    email = Messaging.email_from_name(name, gameid)
    assert email == '"foo (The Feds)" <foo@1234.planets.nu>'


def test_construct_msg_id(message_no_replies):
    msg_id = Messaging.construct_msg_id(message_no_replies)
    assert msg_id == "<4847926.0@374955.planets.nu>"
