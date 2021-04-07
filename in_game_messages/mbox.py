# -*- coding: utf-8 -*-
"""Mailbox module for storing in-game messages."""

import datetime
import email
import logging
import mailbox
from pathlib import Path
from typing import Dict


class Mbox:
    """A utility class used to handle faux e-mail messages."""

    def __init__(
        self,
        mbox_path: Path,
    ) -> None:
        """Class constructor."""
        super().__init__()
        self.mbox = mailbox.mbox(mbox_path, create=True)
        self.logger = logging.getLogger(__name__)

    def get_message_ids(self) -> Dict:
        """Return message IDs from a mailbox."""
        message_ids = {}
        for message in self.mbox.itervalues():
            message_ids[message["Message-ID"]] = message["X-Slack-ID"]
        return message_ids

    def save_email_message(
        self,
        message: Dict,
        thread_id: str = None,
    ) -> bool:
        """Construct an e-mail from an in-game message and save it to a mailbox."""
        try:
            # Construct the message and save to mailbox
            msg = email.message.EmailMessage()
            msg["From"] = message["sender"]["email"]
            msg["To"] = ", ".join(message["recipients"].values())
            msg["Subject"] = f"Turn {message['turn']}"
            msg["Message-ID"] = message["msgid"]
            msg["X-Slack-ID"] = thread_id
            msg["Thread-Index"] = message["threadindex"]
            msg["Thread-Topic"] = message["threadtopic"]
            msg["Date"] = datetime.datetime.strptime(
                message["dateadded"], "%Y-%m-%dT%H:%M:%S"
            )
            msg.set_content(str(message["message"].replace("<br/>", "\n")))
            if "parentmsgid" in message:
                msg["References"] = message["parentmsgid"]
                msg["In-Reply-To"] = message["parentmsgid"]
            self.mbox.add(msg)
            return True
        except mailbox.Error as err:
            self.logger.error("Saving message to mailbox failed: %s", err)
            return False
