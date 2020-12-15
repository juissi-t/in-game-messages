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


class Messaging:
    """TODO: add class docstring"""

    def __init__(self, planets_api_key: str) -> None:
        super().__init__()
        self.planets_api_key = planets_api_key
        self.logger = logging.getLogger(__name__)

    def get_messages_from_game(
        self, planets_game_id: str, planets_race_id: str
    ) -> List:
        """Get messages for a single race from a game."""
        payload = {
            "apikey": self.planets_api_key,
            "gameid": planets_game_id,
            "playerid": planets_race_id,
        }

        resp = requests.post(
            "https://api.planets.nu/account/ingameactivity", data=payload
        )

        if "activity" in resp.json():
            messages = []
            for message in sorted(resp.json()["activity"], key=lambda x: x["orderid"]):
                message["msgid"] = construct_msg_id(message)
                participants = get_message_participants(message)
                # Remove sender from the recipients list. Don't care if something fails.
                recipients = participants.copy()
                if len(recipients) > 1:
                    try:
                        del recipients[message["sourcename"]]
                    except KeyError:
                        pass
                message["recipients"] = recipients
                message["replies"] = []
                for reply in message["_replies"]:
                    reply["parentid"] = message["msgid"]
                    reply["msgid"] = construct_msg_id(reply)
                    reply_recipients = participants.copy()
                    if len(reply_recipients) > 1:
                        try:
                            del reply_recipients[reply["sourcename"]]
                        except KeyError:
                            pass
                    reply["recipients"] = reply_recipients
                    message["replies"].append(reply)
                messages.append(message)
            return messages

        self.logger.info("No messages found. Response: %s", resp.json())
        return []

    def get_all_messages_from_game(self, planets_game_id: str) -> List:
        """Get messages for all races from a game."""
        messages = []
        for race_id in self.get_race_ids_for_game(planets_game_id):
            messages.append(self.get_messages_from_game(planets_game_id, race_id))
        return messages

    def get_race_ids_for_game(self, planets_game_id: str) -> List:
        """Get race IDs from a game."""
        race_ids = []
        payload = {"apikey": self.planets_api_key, "gameid": planets_game_id}
        resp = requests.post(
            "https://api.planets.nu/game/loadinfo?version=1", data=payload
        )
        if "players" in resp.json():
            for player in resp.json()["players"]:
                race_ids.append(player["raceid"])
        else:
            self.logger.info("No races found for game %s.", planets_game_id)
        return race_ids


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
                        construct_slack_message(msg),
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
                        construct_slack_message(reply),
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
            msg["From"] = email_from_name(message["sourcename"], message["gameid"])
            msg["To"] = ", ".join(message["recipients"].values())
            msg["Subject"] = f"Turn {message['turn']}"
            msg["Message-ID"] = message["msgid"]
            msg["X-Slack-ID"] = thread_id
            msg["Date"] = datetime.datetime.strptime(
                message["dateadded"], "%Y-%m-%dT%H:%M:%S"
            )
            msg.set_content(str(message["message"].replace("<br/>", "\n")))
            if message["parentid"]:
                msg["References"] = message["parentid"]
                msg["In-Reply-To"] = message["parentid"]
            mbox.add(msg)
            return True
        except mailbox.Error as err:
            self.logger.error("Saving message to mailbox failed: %s", err)
            return False


def construct_slack_message(message: Dict) -> str:
    """Construct a Slack message from an in-game message."""
    turn_str = f'*Turn {message["turn"]}*'
    to_str = f'*To:* {", ".join(message["recipients"].keys())}'
    date_str = f'*Date*: {message["dateadded"]}'
    body_str = message["message"].replace("<br/>", "\n")
    return f"{turn_str}\n{to_str}\n{date_str}\n\n{body_str}"


def construct_msg_id(message: Dict) -> str:
    """Construct a unique message ID for an in-game message."""
    msg_id = str(message["id"])
    order_id = str(message["orderid"])
    parent_id = str(message["parentid"])
    return f"<{msg_id}.{order_id}.{parent_id}@{message['gameid']}.planets.nu>"


def get_message_participants(message: Dict) -> Dict:
    """Get a dict of message participants and their faux emails."""
    # Create a participants list with both sender and recipients
    participants = {}
    for name in message["targetname"].split(","):
        participants[name.strip()] = email_from_name(name.strip(), message["gameid"])
    participants[message["sourcename"]] = email_from_name(
        message["sourcename"], message["gameid"]
    )
    return participants


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
