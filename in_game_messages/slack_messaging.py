# -*- coding: utf-8 -*-
"""Slack Messaging module and for sending in-game messages to Slack."""

import datetime
import email
import logging
import mailbox
import re
import time
from typing import Dict, List

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse


class SlackMessaging:
    """A class used to parse in-game messages and send them to Slack."""

    def __init__(
        self,
        slack_bot_token: str,
        slack_channel_id: str,
    ) -> None:
        super().__init__()
        self.slack_channel_id = slack_channel_id
        self.slack_client = WebClient(token=slack_bot_token)
        self.logger = logging.getLogger(__name__)

    def send_slack_message(
        self, text: str, sender_name: str, parent: str = None
    ) -> SlackResponse:
        """Send Slack message to the configured channel."""
        try:
            # Call the chat.postMessage method using the WebClient
            result = self.slack_client.chat_postMessage(
                channel=self.slack_channel_id,
                text=text,
                username=sender_name,
                icon_url=self.icon_from_name(sender_name),
                thread_ts=parent,
            )
            self.logger.debug(result)
            return result

        except SlackApiError as err:
            self.logger.error("Error posting message: %s", err)
            raise

    def send_new_messages_to_slack(self, messages: List, planets_game_id: str) -> None:
        """Fetch messages from a game and send new ones to Slack."""
        mbox = mailbox.mbox(f"messages-{planets_game_id}.mbox", create=True)
        message_ids = {}

        # If the mbox file already exists, find all the message IDs and
        # add them to the list so that we don't push duplicates to the mbox.
        for message in mbox.itervalues():
            message_ids[message["Message-ID"]] = message["X-Slack-ID"]

        for msg in messages:
            slack_thread_id = None
            # Check that we haven't sent the message earlier, and filter out
            # some spammy messages generated by the system.
            if msg["msgid"] not in message_ids:
                if not (
                    msg["sourcename"] == msg["gamename"]
                    and len(msg["replies"]) == 0
                    and re.search(
                        "joined the game in slot|earned the award", msg["message"]
                    )
                ):
                    # Let's not overwhelm Slack API
                    time.sleep(2)

                    # Construct the Slack message and send it
                    slack_resp = self.send_slack_message(
                        self.construct_slack_message(msg),
                        msg["sourcename"],
                    )

                    if slack_resp:
                        self.logger.info(
                            "Message %s sent to Slack successfully.", msg["msgid"]
                        )
                        slack_thread_id = slack_resp["ts"]
                        if self.save_email_message(mbox, msg, slack_thread_id):
                            message_ids[msg["msgid"]] = slack_thread_id
            else:
                self.logger.debug("Message %s already sent.", msg["msgid"])
                slack_thread_id = message_ids[msg["msgid"]]

            for reply in sorted(msg["replies"], key=lambda x: x["dateadded"]):
                if reply["msgid"] not in message_ids:
                    # Let's not overwhelm Slack API
                    time.sleep(2)

                    # Construct the Slack message and send it
                    slack_reply_resp = self.send_slack_message(
                        self.construct_slack_message(reply),
                        reply["sourcename"],
                        slack_thread_id,
                    )

                    if slack_reply_resp:
                        self.logger.info(
                            "Reply %s (parent %s) sent to Slack successfully.",
                            reply["msgid"],
                            msg["msgid"],
                        )
                        if self.save_email_message(
                            mbox,
                            reply,
                            slack_reply_resp["ts"],
                        ):
                            message_ids[reply["msgid"]] = slack_thread_id
                else:
                    self.logger.debug(
                        "Reply %s (parent %s) already sent.",
                        reply["msgid"],
                        msg["msgid"],
                    )

    def save_email_message(
        self,
        mbox: mailbox.Mailbox,
        message: Dict,
        thread_id: str,
    ) -> bool:
        """Construct an e-mail from an in-game message and save it to a mailbox."""
        try:
            # Construct the message and save to mailbox
            msg = email.message.EmailMessage()
            msg["From"] = message["sender"]
            msg["To"] = ", ".join(message["recipients"].values())
            msg["Subject"] = f"Turn {message['turn']}"
            msg["Message-ID"] = message["msgid"]
            msg["X-Slack-ID"] = thread_id
            msg["Date"] = datetime.datetime.strptime(
                message["dateadded"], "%Y-%m-%dT%H:%M:%S"
            )
            msg.set_content(str(message["message"].replace("<br/>", "\n")))
            if "parentmsgid" in message:
                msg["References"] = message["parentmsgid"]
                msg["In-Reply-To"] = message["parentmsgid"]
            mbox.add(msg)
            return True
        except mailbox.Error as err:
            self.logger.error("Saving message to mailbox failed: %s", err)
            return False

    @staticmethod
    def construct_slack_message(message: Dict) -> str:
        """Construct a Slack message from an in-game message."""
        turn_str = f'*Turn {message["turn"]}*'
        to_str = f'*To:* {", ".join(message["recipients"].keys())}'
        date_str = f'*Date*: {message["dateadded"]}'
        body_str = message["message"].replace("<br/>", "\n")
        return f"{turn_str}\n{to_str}\n{date_str}\n\n{body_str}"

    @staticmethod
    def icon_from_name(name: str) -> str:
        """Return an icon URL from in-game name."""
        base_url = "https://mobile.planets.nu/img/"
        races = {
            "The Feds": 1,
            "The Lizards": 2,
            "The Bird Men": 3,
            "The Fascists": 4,
            "The Privateers": 5,
            "The Cyborg": 6,
            "The Crystals": 7,
            "The Evil Empire": 8,
            "The Robots": 9,
            "The Rebels": 10,
            "The Colonies": 11,
            "The Horwasp": 12,
        }

        for race_name, race_id in races.items():
            if name.endswith(f"({race_name})"):
                return f"{base_url}races/race-{str(race_id)}.jpg"

        return f"{base_url}ui/league-logo-400-drop.png"
