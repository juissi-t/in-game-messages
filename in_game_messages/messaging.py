# -*- coding: utf-8 -*-
"""Messaging module and helper utilities for sending in-game messages to Slack."""

import datetime
import email
import logging
import mailbox
import re
import time
from typing import Dict, List

import requests
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
                icon_url=icon_from_name(sender_name),
                thread_ts=parent,
            )
            self.logger.debug(result)
            return result

        except SlackApiError as err:
            self.logger.error("Error posting message: %s", err)
            raise

    def send_new_messages_to_slack(
        self, planets_api_key: str, planets_game_id: str, planets_race_id: str
    ) -> None:
        """Fetch messages from a game and send new ones to Slack."""
        mbox = mailbox.mbox(f"messages-{planets_game_id}.mbox", create=True)
        message_ids = {}

        # If the mbox file already exists, find all the message IDs and
        # add them to the list so that we don't push duplicates to the mbox.
        for message in mbox.itervalues():
            message_ids[message["Message-ID"]] = message["X-Slack-ID"]

        payload = {
            "apikey": planets_api_key,
            "gameid": planets_game_id,
            "playerid": planets_race_id,
        }

        resp = requests.post(
            "https://api.planets.nu/account/ingameactivity", data=payload
        )

        if "activity" not in resp.json():
            self.logger.info("No messages found. Response: %s", resp.json())
            return

        for msg in sorted(resp.json()["activity"], key=lambda x: x["orderid"]):
            # Create a unique ID for not adding duplicates
            msg_id = construct_msg_id(msg)

            # Create a participants list with both sender and recipients
            participants_email = [
                email_from_name(i.strip(), planets_game_id)
                for i in msg["targetname"].split(",")
            ]
            participants_email.append(
                email_from_name(msg["sourcename"], planets_game_id)
            )
            participants = [i.strip() for i in msg["targetname"].split(",")]
            participants.append(msg["sourcename"])

            slack_thread_id = None
            if msg_id not in message_ids:
                # Decide if this message is needed
                if (
                    msg["sourcename"] == msg["gamename"]
                    and not msg["_replies"]
                    and re.search(
                        "joined the game in slot|earned the award", msg["message"]
                    )
                ):
                    continue

                # Let's not overwhelm Slack API
                time.sleep(2)
                # Remove sender from the recipients list. Don't care if something fails.
                recipients_email = participants_email.copy()
                recipients = participants.copy()
                if len(recipients) > 1:
                    try:
                        recipients_email.remove(
                            email_from_name(msg["sourcename"], planets_game_id)
                        )
                        recipients.remove(msg["sourcename"])
                    except ValueError:
                        pass

                # Construct the Slack message and send it
                slack_resp = self.send_slack_message(
                    construct_slack_message(msg, recipients),
                    msg["sourcename"],
                )

                if slack_resp:
                    self.logger.info("Message %s sent to Slack successfully.", msg_id)
                    slack_thread_id = slack_resp["ts"]
                    if self.save_email_message(
                        mbox, msg, recipients_email, msg_id, slack_thread_id
                    ):
                        message_ids[msg_id] = slack_thread_id
            else:
                self.logger.debug("Message %s already sent.", msg_id)
                slack_thread_id = message_ids[msg_id]

            for reply in sorted(msg["_replies"], key=lambda x: x["dateadded"]):
                # Create a unique ID for not adding duplicates
                reply_id = construct_msg_id(reply)

                if reply_id not in message_ids:
                    # Let's not overwhelm Slack API
                    time.sleep(2)
                    # Remove sender from the recipients list. Don't care if it fails.
                    recipients_email = participants_email.copy()
                    recipients = participants.copy()
                    if len(recipients) > 1:
                        try:
                            recipients_email.remove(
                                email_from_name(reply["sourcename"], planets_game_id)
                            )
                            recipients.remove(reply["sourcename"])
                        except ValueError:
                            pass

                    # Construct the Slack message and send it
                    slack_reply_resp = self.send_slack_message(
                        construct_slack_message(reply, recipients),
                        reply["sourcename"],
                        slack_thread_id,
                    )

                    if slack_reply_resp:
                        self.logger.info(
                            "Reply %s (parent %s) sent to Slack successfully.",
                            reply_id,
                            msg_id,
                        )
                        if self.save_email_message(
                            mbox,
                            reply,
                            recipients_email,
                            reply_id,
                            slack_reply_resp["ts"],
                            msg_id,
                        ):
                            message_ids[reply_id] = slack_thread_id
                else:
                    self.logger.debug(
                        "Reply %s (parent %s) already sent.", reply_id, msg_id
                    )

    # pylint: disable=too-many-arguments
    def save_email_message(
        self,
        mbox: mailbox.Mailbox,
        message: Dict,
        recipients: List,
        msg_id: str,
        thread_id: str,
        parent_msg_id: str = "",
    ) -> bool:
        """Construct an e-mail from an in-game message and save it to a mailbox."""
        try:
            # Construct the message and save to mailbox
            msg = email.message.EmailMessage()
            msg["From"] = email_from_name(message["sourcename"], message["gameid"])
            msg["To"] = ", ".join(list(set(recipients)))
            msg["Subject"] = f"Turn {message['turn']}"
            msg["Message-ID"] = msg_id
            msg["X-Slack-ID"] = thread_id
            msg["Date"] = datetime.datetime.strptime(
                message["dateadded"], "%Y-%m-%dT%H:%M:%S"
            )
            msg.set_content(str(message["message"].replace("<br/>", "\n")))
            if parent_msg_id:
                msg["References"] = parent_msg_id
                msg["In-Reply-To"] = parent_msg_id
            mbox.add(msg)
            return True
        except mailbox.Error as err:
            self.logger.error("Saving message to mailbox failed: %s", err)
            return False


def construct_slack_message(message: Dict, recipients: List) -> str:
    """Construct a Slack message from an in-game message."""
    turn_str = f'*Turn {message["turn"]}*'
    to_str = f'*To:* {", ".join(list(set(recipients)))}'
    date_str = f'*Date*: {message["dateadded"]}'
    body_str = message["message"].replace("<br/>", "\n")
    return f"{turn_str}\n{to_str}\n{date_str}\n\n{body_str}"


def construct_msg_id(message: Dict) -> str:
    """Construct a unique message ID for an in-game message."""
    msg_id = str(message["id"])
    order_id = str(message["orderid"])
    parent_id = str(message["parentid"])
    return f"<{msg_id}.{order_id}.{parent_id}@{message['gameid']}.planets.nu>"


def email_from_name(name: str, game_id: str) -> str:
    """Create a faux e-mail address from an in-game name."""
    address = re.sub(r"\([^()]*\)", "", name)
    return f'"{name}" <{address.replace(" ", "")}@{game_id}.planets.nu>'


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
