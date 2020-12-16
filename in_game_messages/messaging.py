# -*- coding: utf-8 -*-
"""Messaging module and helper utilities for fetching in-game messages."""

import logging
import re
from typing import Dict, List

import requests


class Messaging:
    """A class to fetch messages for a game from planets.nu."""

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
                message["msgid"] = self.construct_msg_id(message)
                participants = self.get_message_participants(message)
                # Remove sender from the recipients list. Don't care if something fails.
                recipients = participants.copy()
                if len(recipients) > 1:
                    try:
                        del recipients[message["sourcename"]]
                    except KeyError:
                        pass
                message["recipients"] = recipients
                message["sender"] = self.email_from_name(
                    message["sourcename"], message["gameid"]
                )
                message["replies"] = []
                for reply in message["_replies"]:
                    reply["parentmsgid"] = message["msgid"]
                    reply["msgid"] = self.construct_msg_id(reply)
                    reply_recipients = participants.copy()
                    if len(reply_recipients) > 1:
                        try:
                            del reply_recipients[reply["sourcename"]]
                        except KeyError:
                            pass
                    reply["recipients"] = reply_recipients
                    reply["sender"] = self.email_from_name(
                        reply["sourcename"], reply["gameid"]
                    )
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
        return sorted(messages, key=lambda x: x["orderid"])

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

    def get_message_participants(self, message: Dict) -> Dict:
        """Get a dict of message participants and their faux emails."""
        # Create a participants list with both sender and recipients
        participants = {}
        for name in message["targetname"].split(","):
            participants[name.strip()] = self.email_from_name(
                name.strip(), message["gameid"]
            )
        participants[message["sourcename"]] = self.email_from_name(
            message["sourcename"], message["gameid"]
        )
        return participants

    @staticmethod
    def construct_msg_id(message: Dict) -> str:
        """Construct a unique message ID for an in-game message."""
        msg_id = str(message["id"])
        order_id = str(message["orderid"])
        parent_id = str(message["parentid"])
        return f"<{msg_id}.{order_id}.{parent_id}@{message['gameid']}.planets.nu>"

    @staticmethod
    def email_from_name(name: str, game_id: str) -> str:
        """Create a faux e-mail address from an in-game name."""
        address = re.sub(r"\([^()]*\)", "", name)
        return f'"{name}" <{address.replace(" ", "")}@{game_id}.planets.nu>'
