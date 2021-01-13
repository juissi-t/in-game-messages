from in_game_messages.exporting import Exporting

import pytest
import mailbox


def test_to_csv(tmp_path, full_message):
    exp = Exporting()
    exp.to_csv([full_message], tmp_path / "csv")
    count = 0
    with open(tmp_path / "csv", "r") as f:
        for _ in f:
            count += 1
    # We should have 6 lines because the message contains newlines
    assert count == 6


def test_to_mbox(tmp_path, full_message):
    exp = Exporting()
    exp.to_mbox([full_message], tmp_path / "mbox")
    mailbox_mbox = mailbox.mbox(tmp_path / "mbox")
    assert mailbox_mbox.__len__() == 1
