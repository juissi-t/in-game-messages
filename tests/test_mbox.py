import mailbox

import pytest
from tests.conftest import message_no_replies

from in_game_messages.mbox import Mbox


def test_get_message_ids(tmp_path, full_message):
    mbox = Mbox(tmp_path / "mbox")
    mbox.save_email_message(full_message)
    message_ids = mbox.get_message_ids()
    assert len(message_ids) == 1
    assert "<4847926.0@374955.planets.nu>" in message_ids


def test_save_email_message(tmp_path, full_message):
    mbox = Mbox(tmp_path / "mbox")
    mbox.save_email_message(full_message)
    mailbox_mbox = mailbox.mbox(tmp_path / "mbox")
    assert mailbox_mbox.__len__() == 1
    _, message = mailbox_mbox.popitem()
    assert message["From"] == '"tom n (The Lizards)" <tomn@374955.planets.nu>'
