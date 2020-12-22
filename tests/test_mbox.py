import mailbox
from in_game_messages.mbox import Mbox


def test_get_message_ids(tmp_path, message_no_replies, sender):
    mbox = Mbox(tmp_path / "mbox")
    message_no_replies["sender"] = sender
    message_no_replies["recipients"] = {
        "coen1970 (The Colonies)": '"coen1970 (The Colonies)" <coen1970@374955.planets.nu>'
    }
    message_no_replies["msgid"] = "<4847926.0@374955.planets.nu>"
    mbox.save_email_message(message_no_replies, "1")
    message_ids = mbox.get_message_ids()
    assert len(message_ids) == 1
    assert "<4847926.0@374955.planets.nu>" in message_ids


def test_save_email_message(tmp_path, message_no_replies, sender):
    mbox = Mbox(tmp_path / "mbox")
    message_no_replies["sender"] = sender
    message_no_replies["recipients"] = {
        "coen1970 (The Colonies)": '"coen1970 (The Colonies)" <coen1970@374955.planets.nu>'
    }
    message_no_replies["msgid"] = "<4847926.0@374955.planets.nu>"
    mbox.save_email_message(message_no_replies, "1")
    mailbox_mbox = mailbox.mbox(tmp_path / "mbox")
    assert mailbox_mbox.__len__() == 1
    _, message = mailbox_mbox.popitem()
    assert message["From"] == '"tom n (The Lizards)" <tomn@374955.planets.nu>'
