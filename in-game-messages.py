import os
import logging
import mailbox
import email
import datetime
import requests
import re
import time

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger("in_game_messages")
logger.setLevel(logging.INFO)

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
slack_channel_id = os.environ.get("SLACK_CHANNEL_ID")
planets_api_key = os.environ.get("PLANETS_API_KEY")
planets_game_id = os.environ.get("PLANETS_GAME_ID")
planets_race_id = os.environ.get("PLANETS_RACE_ID")
mbox_file = f"messages-{planets_game_id}.mbox"


def send_slack_message(
    channel_id: str, text: str, sender_name: str, client: WebClient, parent: str = None
):
    try:
        # Call the chat.postMessage method using the WebClient
        result = client.chat_postMessage(
            channel=channel_id,
            text=text,
            username=sender_name,
            icon_url=icon_from_name(sender_name),
            thread_ts=parent,
        )
        logger.info(result)
        return result

    except SlackApiError as e:
        logger.error(f"Error posting message: {e}")
        return False


def send_new_messages_to_slack(mbox_file: str, race: str, api_key: str, game_id: int):
    mb = mailbox.mbox(mbox_file, create=True)
    message_ids = {}

    # If the mbox file already exists, find all the message IDs and
    # add them to the list so that we don't push duplicates to the mbox.
    for msg in mb.itervalues():
        message_ids[msg["Message-ID"]] = msg["X-Slack-ID"]

    payload = {
        "apikey": api_key,
        "gameid": game_id,
        "playerid": race,
    }

    resp = requests.post("https://api.planets.nu/account/ingameactivity", data=payload)

    if "activity" in resp.json():
        for msg in sorted(resp.json()["activity"], key=lambda x: x["orderid"]):
            if msg["turn"] > 10:
                continue
            # Create a unique ID for not adding duplicates
            msg_id = f"<{str(msg['id'])}.{str(msg['orderid'])}.{str(msg['parentid'])}@{game_id}.planets.nu>"

            # Create a participants list with both sender and recipients
            participants_email = [
                email_address_from_name(i.strip(), game_id)
                for i in msg["targetname"].split(",")
            ]
            participants_email.append(
                email_address_from_name(msg["sourcename"], game_id)
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
                            email_address_from_name(msg["sourcename"], game_id)
                        )
                        to.remove(msg["sourcename"])
                    except ValueError:
                        pass

                # Construct the Slack message and send it
                msg_str = msg["message"].replace("<br/>", "\n")
                slack_msg = f'*Turn {msg["turn"]}*\n*To:* {", ".join(list(set(to)))}\n*Date*: {msg["dateadded"]}\n\n{msg_str}'
                slack_resp = send_slack_message(
                    slack_channel_id, slack_msg, msg["sourcename"], client
                )

                if slack_resp:
                    slack_thread_id = slack_resp["ts"]
                    # Construct the message and save to mailbox
                    m = email.message.EmailMessage()
                    m["From"] = email_address_from_name(msg["sourcename"], game_id)
                    m["To"] = ", ".join(list(set(to_email)))
                    m["Subject"] = f"Turn {msg['turn']}"
                    m["Message-ID"] = msg_id
                    m["X-Slack-ID"] = slack_thread_id
                    m["Date"] = datetime.datetime.strptime(
                        msg["dateadded"], "%Y-%m-%dT%H:%M:%S"
                    )
                    m.set_content(str(msg["message"].replace("<br/>", "\n")))
                    mb.add(m)
                    message_ids[msg_id] = slack_thread_id
            else:
                slack_thread_id = message_ids[msg_id]

            for reply in sorted(msg["_replies"], key=lambda x: x["dateadded"]):
                # Create a unique ID for not adding duplicates
                reply_id = f"<{str(reply['id'])}.{str(reply['orderid'])}.{str(reply['parentid'])}@{game_id}.planets.nu>"

                if reply_id not in message_ids:
                    # Let's not overwhelm Slack API
                    time.sleep(2)
                    # Remove sender from the recipients list. Don't care if something fails.
                    to_email = participants_email.copy()
                    to = participants.copy()
                    if len(to) > 1:
                        try:
                            to_email.remove(
                                email_address_from_name(reply["sourcename"], game_id)
                            )
                            to.remove(reply["sourcename"])
                        except ValueError:
                            pass

                    # Construct the Slack message and send it
                    reply_str = reply["message"].replace("<br/>", "\n")
                    slack_msg = f'*Turn {reply["turn"]}*\n*To:* {", ".join(list(set(to)))}\n*Date*: {reply["dateadded"]}\n\n{reply_str}'
                    slack_reply_resp = send_slack_message(
                        slack_channel_id,
                        slack_msg,
                        reply["sourcename"],
                        client,
                        slack_thread_id,
                    )

                    if slack_reply_resp:
                        # Construct the reply and save to mailbox
                        r = email.message.EmailMessage()
                        r["From"] = email_address_from_name(
                            reply["sourcename"], game_id
                        )
                        r["To"] = ", ".join(list(set(to_email)))
                        r["Subject"] = f"Turn {reply['turn']}"
                        r["Message-ID"] = reply_id
                        r["X-Slack-ID"] = slack_thread_id
                        r["Date"] = datetime.datetime.strptime(
                            reply["dateadded"], "%Y-%m-%dT%H:%M:%S"
                        )
                        r["References"] = msg_id
                        r["In-Reply-To"] = msg_id
                        r.set_content(str(reply["message"].replace("<br/>", "\n")))
                        mb.add(r)
                        message_ids[reply_id] = slack_thread_id

    # Close the mailbox to flush writes
    mb.close()


def email_address_from_name(name: str, game_id: str):
    email = re.sub(r"\([^()]*\)", "", name)
    return f'"{name}" <{email.replace(" ", "")}@{game_id}.planets.nu>'


def icon_from_name(name: str):
    base_url = "https://mobile.planets.nu/img/"
    # "race-{race}.jpg"

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


send_new_messages_to_slack(mbox_file, planets_race_id, planets_api_key, planets_game_id)
