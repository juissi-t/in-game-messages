import requests

from in_game_messages.messaging import Messaging


def test_get_messages_from_game(monkeypatch, all_messages):
    class MockResponseMessages:
        @staticmethod
        def json():
            return all_messages

    def mock_post(*args, **kwargs):
        return MockResponseMessages()

    monkeypatch.setattr(requests, "post", mock_post)

    messaging = Messaging("abcd")
    messages = messaging.get_messages_from_game("1234", "2")
    assert isinstance(messages, list)
    assert len(messages) == 2


def test_get_messages_from_game_no_messages(monkeypatch, no_messages):
    class MockResponseMessages:
        @staticmethod
        def json():
            return no_messages

    def mock_post(*args, **kwargs):
        return MockResponseMessages()

    monkeypatch.setattr(requests, "post", mock_post)

    messaging = Messaging("abcd")
    messages = messaging.get_messages_from_game("1234", "2")
    assert isinstance(messages, list)
    assert len(messages) == 0


def test_get_all_messages_from_game(monkeypatch, all_messages):
    class MockResponseMessages:
        @staticmethod
        def json():
            return all_messages

    def mock_race_ids(self, planets_game_id):
        return ["2", "11"]

    def mock_post(*args, **kwargs):
        return MockResponseMessages()

    monkeypatch.setattr(Messaging, "get_race_ids_for_game", mock_race_ids)
    monkeypatch.setattr(requests, "post", mock_post)

    messaging = Messaging("abcd")
    messages = messaging.get_all_messages_from_game("1234")
    assert isinstance(messages, list)
    assert len(messages) == 4


def test_get_race_ids_for_game(monkeypatch):
    class MockResponseLoadinfo:
        @staticmethod
        def json():
            return {"players": [{"raceid": "2"}, {"raceid": "11"}]}

    def mock_post(*args, **kwargs):
        return MockResponseLoadinfo()

    monkeypatch.setattr(requests, "post", mock_post)

    messaging = Messaging("abcd")
    race_ids = messaging.get_race_ids_for_game("1234")
    assert race_ids == ["2", "11"]


def test_get_message_participants(message_no_replies):
    messaging = Messaging("abcd")
    participants = messaging.get_message_participants(message_no_replies)
    assert len(participants) == 2
    assert isinstance(participants, dict)
    assert "coen1970 (The Colonies)" in participants
    assert (
        participants["coen1970 (The Colonies)"]
        == '"coen1970 (The Colonies)" <coen1970@374955.planets.nu>'
    )


def test_get_system_message_participants(message_with_reply):
    messaging = Messaging("abcd")
    participants = messaging.get_message_participants(message_with_reply)
    assert len(participants) == 1
    assert isinstance(participants, dict)
    assert "Leshy Sector" in participants
    assert (
        participants["Leshy Sector"] == '"Leshy Sector" <LeshySector@374955.planets.nu>'
    )


def test_email_from_name():
    name = "foo (The Feds)"
    gameid = "1234"
    email = Messaging.email_from_name(name, gameid)
    assert email == '"foo (The Feds)" <foo@1234.planets.nu>'


def test_construct_msg_id(message_no_replies):
    msg_id = Messaging.construct_msg_id(message_no_replies)
    assert msg_id == "<4847926.0@374955.planets.nu>"


def test_construct_outlook_thread_index(message_with_reply):
    messaging = Messaging("abcd")
    thread_index = messaging.construct_outlook_thread_index(message_with_reply)
    assert thread_index == "AdZAbj23ui+pCroMkYwvKHLiyERMhA=="
    reply = message_with_reply["_replies"][0]
    reply_thread_index = messaging.construct_outlook_thread_index(reply, thread_index)
    assert reply_thread_index == "AdZAbj23ui+pCroMkYwvKHLiyERMhAADorox"


def test_icon_from_message(message_no_replies):
    icons = Messaging.icon_from_message(message_no_replies)
    assert len(icons) == 3
    assert (
        icons["league"] == "https://mobile.planets.nu/img/ui/league-logo-400-drop.png"
    )
    assert icons["player"] == "https://profiles2.planets.nu/5635"
    assert icons["race"] == "https://mobile.planets.nu/img/races/race-2.jpg"
