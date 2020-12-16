import pytest

from in_game_messages.messaging import Messaging


def test_email_from_name():
    name = "foo (The Feds)"
    gameid = "1234"
    email = Messaging.email_from_name(name, gameid)
    assert email == '"foo (The Feds)" <foo@1234.planets.nu>'


def test_construct_msg_id():
    message = {
        "id": "1",
        "orderid": "2",
        "parentid": "0",
        "gameid": "1234",
    }
    msg_id = Messaging.construct_msg_id(message)
    assert msg_id == "<1.2.0@1234.planets.nu>"
