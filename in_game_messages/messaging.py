import mailbox
import email
import datetime
from typing import Dict, List
import logging
import requests
import re
import time
import sys

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Messaging:
    def __init__(
        self,
        slack_bot_token: str,
        slack_channel_id: str,
        planets_api_key: str,
        planets_game_id: str,
        planets_race_id: str,
    ) -> None:
        super().__init__()
        self.slack_bot_token = slack_bot_token
        self.slack_channel_id = slack_channel_id
        self.planets_api_key = planets_api_key
        self.planets_game_id = planets_game_id
        self.planets_race_id = planets_race_id
        self.mbox_file = f"messages-{planets_game_id}.mbox"

        self.slack_client = WebClient(token=self.slack_bot_token)
        self.logger = logging.getLogger(__name__)

    def send_slack_message(
        self, text: str, sender_name: str, parent: str = None
    ) -> Dict:
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

        except SlackApiError as e:
            self.logger.error(f"Error posting message: {e}")
            return {}

    def send_new_messages_to_slack(self) -> None:
        """Fetch messages from a game and send new ones to Slack."""
        mb = mailbox.mbox(self.mbox_file, create=True)
        message_ids = {}

        # If the mbox file already exists, find all the message IDs and
        # add them to the list so that we don't push duplicates to the mbox.
        for msg in mb.itervalues():
            message_ids[msg["Message-ID"]] = msg["X-Slack-ID"]

        payload = {
            "apikey": self.planets_api_key,
            "gameid": self.planets_game_id,
            "playerid": self.planets_race_id,
        }

        resp = requests.post(
            "https://api.planets.nu/account/ingameactivity", data=payload
        )

        if "activity" in resp.json():
            for msg in sorted(resp.json()["activity"], key=lambda x: x["orderid"]):
                # Create a unique ID for not adding duplicates
                msg_id = self.construct_msg_id(msg)

                # Create a participants list with both sender and recipients
                participants_email = [
                    self.email_from_name(i.strip(), self.planets_game_id)
                    for i in msg["targetname"].split(",")
                ]
                participants_email.append(
                    self.email_from_name(msg["sourcename"], self.planets_game_id)
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
                    to_email = participants_email.copy()
                    to = participants.copy()
                    if len(to) > 1:
                        try:
                            to_email.remove(
                                self.email_from_name(
                                    msg["sourcename"], self.planets_game_id
                                )
                            )
                            to.remove(msg["sourcename"])
                        except ValueError:
                            pass

                    # Construct the Slack message and send it
                    slack_resp = self.send_slack_message(
                        self.construct_slack_message(msg, to),
                        msg["sourcename"],
                    )

                    if slack_resp:
                        self.logger.info(
                            f"Message {msg_id} sent to Slack successfully."
                        )
                        slack_thread_id = slack_resp["ts"]
                        if self.save_email_message(
                            mb, msg, to_email, msg_id, slack_thread_id
                        ):
                            message_ids[msg_id] = slack_thread_id
                else:
                    self.logger.debug(f"Message {msg_id} already sent.")
                    slack_thread_id = message_ids[msg_id]

                for reply in sorted(msg["_replies"], key=lambda x: x["dateadded"]):
                    # Create a unique ID for not adding duplicates
                    reply_id = self.construct_msg_id(reply)

                    if reply_id not in message_ids:
                        # Let's not overwhelm Slack API
                        time.sleep(2)
                        # Remove sender from the recipients list. Don't care if something fails.
                        to_email = participants_email.copy()
                        to = participants.copy()
                        if len(to) > 1:
                            try:
                                to_email.remove(
                                    self.email_from_name(
                                        reply["sourcename"], self.planets_game_id
                                    )
                                )
                                to.remove(reply["sourcename"])
                            except ValueError:
                                pass

                        # Construct the Slack message and send it
                        slack_reply_resp = self.send_slack_message(
                            self.construct_slack_message(reply, to),
                            reply["sourcename"],
                            slack_thread_id,
                        )

                        if slack_reply_resp:
                            self.logger.info(
                                f"Reply {reply_id} (parent {msg_id}) sent to Slack successfully."
                            )
                            if self.save_email_message(
                                mb, reply, to_email, reply_id, slack_reply_resp["ts"]
                            ):
                                message_ids[reply_id] = slack_thread_id
                    else:
                        self.logger.debug(
                            f"Reply {reply_id} (parent {msg_id}) already sent."
                        )
        else:
            self.logger.info(f"No messages found. Response: {resp.json()}")

        # Close the mailbox to flush writes
        mb.close()

    def save_email_message(
        self,
        mb: mailbox.Mailbox,
        message: Dict,
        to: List,
        msg_id: str,
        thread_id: str,
    ) -> bool:
        """Construct an e-mail message from an in-game message and save it to a mailbox."""
        try:
            # Construct the message and save to mailbox
            m = email.message.EmailMessage()
            m["From"] = self.email_from_name(message["sourcename"], message["gameid"])
            m["To"] = ", ".join(list(set(to)))
            m["Subject"] = f"Turn {message['turn']}"
            m["Message-ID"] = msg_id
            m["X-Slack-ID"] = thread_id
            m["Date"] = datetime.datetime.strptime(
                message["dateadded"], "%Y-%m-%dT%H:%M:%S"
            )
            m.set_content(str(message["message"].replace("<br/>", "\n")))
            mb.add(m)
            return True
        except:
            e = sys.exc_info()[0]
            self.logger.error(f"Saving message to mailbox failed: {e}")
            return False

    def construct_slack_message(_, message: Dict, to: List) -> str:
        """Construct a Slack message from an in-game message."""
        body = message["message"].replace("<br/>", "\n")
        return f'*Turn {message["turn"]}*\n*To:* {", ".join(list(set(to)))}\n*Date*: {message["dateadded"]}\n\n{body}'

    def construct_msg_id(_, message: Dict) -> str:
        """Construct a unique message ID for an in-game message."""
        return f"<{str(message['id'])}.{str(message['orderid'])}.{str(message['parentid'])}@{message['gameid']}.planets.nu>"

    def email_from_name(_, name: str, game_id: str) -> str:
        """Create a faux e-mail address from an in-game name."""
        email = re.sub(r"\([^()]*\)", "", name)
        return f'"{name}" <{email.replace(" ", "")}@{game_id}.planets.nu>'

    def icon_from_name(_, name: str) -> str:
        """Return an icon URL from in-game name."""
        base_url = "https://mobile.planets.nu/img/"
        race = None

        if re.match(".*\(The Feds\)", name):
            race = 1
        elif re.match(".*\(The Lizards\)", name):
            race = 2
        elif re.match(".*\(The Bird Men\)", name):
            race = 3
        elif re.match(".*\(The Fascists\)", name):
            race = 4
        elif re.match(".*\(The Privateers\)", name):
            race = 5
        elif re.match(".*\(The Cyborg\)", name):
            race = 6
        elif re.match(".*\(The Crystals\)", name):
            race = 7
        elif re.match(".*\(The Evil Empire\)", name):
            race = 8
        elif re.match(".*\(The Robots\)", name):
            race = 9
        elif re.match(".*\(The Rebels\)", name):
            race = 10
        elif re.match(".*\(The Colonies\)", name):
            race = 11
        elif re.match(".*\(The Horwasp\)", name):
            race = 12

        if race:
            return f"{base_url}races/race-{str(race)}.jpg"
        else:
            return f"{base_url}ui/league-logo-400-drop.png"
