# -*- coding: utf-8 -*-
"""Cli interface for sending in-game messages to Slack."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from discord import Intents
import requests
import typer

from in_game_messages.discord_messaging import DiscordMessaging
from in_game_messages.exporting import Exporting
from in_game_messages.messaging import Messaging
from in_game_messages.slack_messaging import SlackMessaging

app = typer.Typer()
export_app = typer.Typer()
send_app = typer.Typer()
app.add_typer(export_app, name="export")
app.add_typer(send_app, name="send")

logger = logging.getLogger(__name__)

planets = {
    "api_key": "",
    "game_id": "",
    "race_id": "",
}


@send_app.command()
def slack(
    slack_bot_token: str = typer.Option(..., envvar="SLACK_BOT_TOKEN"),
    slack_channel_id: str = typer.Option(..., envvar="SLACK_CHANNEL_ID"),
):
    """Send planets.nu in-game messages to Slack."""
    if not planets["race_id"]:
        logger.error("Player ID required when sending messages to Slack!")
        raise typer.Exit()
    logger.info("Fetching messages for game %s.", planets["game_id"])
    messaging = Messaging(planets["api_key"])
    messages = messaging.get_messages_from_game(planets["game_id"], planets["race_id"])
    if messages:
        logger.info("Sending messages from game %s to Slack.", planets["game_id"])
        slack_messaging = SlackMessaging(
            slack_bot_token,
            slack_channel_id,
        )
        slack_messaging.send_new_messages_to_slack(messages, planets["game_id"])
        logger.info("Messages sent.")
    else:
        logger.error("Could not get messages from game %s", planets["game_id"])


@send_app.command()
def discord(
    discord_bot_token: str = typer.Option(..., envvar="DISCORD_BOT_TOKEN"),
    discord_channel_id: int = typer.Option(..., envvar="DISCORD_CHANNEL_ID"),
    discord_user_ids: Optional[List[int]] = typer.Option(
        None,
        envvar="DISCORD_USER_IDS",
        help="List of Discord user IDs which will be added to threads",
    ),
):
    """Send planets.nu in-game messages to Discord."""
    if not planets["race_id"]:
        logger.error("Player ID required when sending messages to Discord!")
        raise typer.Exit()
    logger.info("Fetching messages for game %s.", planets["game_id"])
    messaging = Messaging(planets["api_key"])
    messages = messaging.get_messages_from_game(planets["game_id"], planets["race_id"])
    if messages:
        logger.info("Sending messages from game %s to Discord.", planets["game_id"])

        intents = Intents.default()

        discord_messaging = DiscordMessaging(
            discord_channel_id=discord_channel_id,
            discord_user_ids=discord_user_ids,
            game_id=planets["game_id"],
            messages=messages,
            intents=intents,
        )
        discord_messaging.run(token=discord_bot_token)
        logger.info("Messages sent.")
    else:
        logger.error("Could not get messages from game %s", planets["game_id"])


@export_app.command()
def running_to_mbox(
    outdir: Path = typer.Argument(..., help="Directory to store mailbox files in")
):
    """Export planets.nu in-game messages for all your running games to a mailbox."""
    logger.info("Getting list of active games.")
    games = _get_running_games(planets["api_key"])
    logger.info("Found games: %s", ", ".join(games.keys()))
    for game_id, game in games.items():
        outfile = outdir / f"{game['name']} ({game_id})"
        _mbox(game_id, planets["api_key"], game["race"], outfile)


@export_app.command()
def csv(
    outfile: Path = typer.Argument(
        ..., help="Path of the CSV file to use (will be overwritten!)"
    )
):
    """Export planets.nu in-game messages to a CSV (comma-separated values) file."""
    logger.info("Fetching messages for game %s.", planets["game_id"])
    messaging = Messaging(planets["api_key"])
    if planets["race_id"]:
        messages = messaging.get_messages_from_game(
            planets["game_id"], planets["race_id"]
        )
    else:
        messages = messaging.get_all_messages_from_game(planets["game_id"])
    if messages:
        logger.info("Saving messages from game %s to %s.", planets["game_id"], outfile)
        exporting = Exporting()
        exporting.to_csv(messages, outfile)
        logger.info("Messages saved.")
    else:
        logger.error("Could not get messages from game %s", planets["game_id"])


@export_app.command()
def mbox(outfile: Path = typer.Argument(..., help="Path of the mailbox to use")):
    """Export planets.nu in-game messages to a mailbox file."""
    _mbox(planets["game_id"], planets["api_key"], planets["race_id"], outfile)


@app.callback()
@export_app.callback(help="Export in-game messages to various formats.")
@send_app.callback(help="Send in-game messages to instant messaging systems.")
# pylint: disable=too-many-arguments
def main(
    planets_api_key: str = typer.Option(
        default=None,
        envvar="PLANETS_API_KEY",
        help="planets.nu API key (required when not using username and password).",
    ),
    planets_username: str = typer.Option(
        default=None,
        envvar="PLANETS_USERNAME",
        help="planets.nu username (required when not using API key).",
    ),
    planets_password: str = typer.Option(
        default=None,
        envvar="PLANETS_PASSWORD",
        help="planets.nu password (required when not using API key).",
    ),
    planets_race_id: str = typer.Option(
        default=None,
        envvar="PLANETS_RACE_ID",
        help="Race ID to fetch messages for. Fetch for all players if empty"
        "(fetching messages for all players works only for finished games).",
    ),
    planets_game_id: str = typer.Option(
        ...,
        envvar="PLANETS_GAME_ID",
        help="Game ID, found in the game settings or in the game page URL.",
    ),
    debug: bool = typer.Option(False, "--debug"),
):
    """In-game messaging helpers for planets.nu."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        logger.debug("Debug logging enabled.")

    if planets_api_key:
        planets["api_key"] = planets_api_key
    elif planets_username and planets_password:
        planets["api_key"] = _login(planets_username, planets_password)
    else:
        logger.error("Either API key or password and username required!")
        raise typer.Exit()

    planets["game_id"] = planets_game_id
    planets["race_id"] = planets_race_id


def _login(username: str, password: str) -> str:
    """Return planets.nu API key after logging in using username and password."""
    payload = {"username": username, "password": password}
    response = requests.post("https://api.planets.nu/login", data=payload, timeout=30)
    if response.status_code == 200:
        json_doc = response.json()
        if "apikey" in json_doc:
            logger.info("Login to planets.nu successful.")
            return json_doc["apikey"]

    logger.error("Login to planets.nu failed.")
    raise typer.Exit()


def _get_running_games(apikey: str) -> Dict:
    """Return a list of running games for a user."""
    payload = {"apikey": apikey}
    response = requests.post(
        "https://api.planets.nu/account/mygames", data=payload, timeout=30
    )
    if response.status_code == 200:
        json_doc = response.json()
        games = {}
        if "games" in json_doc:
            for game in json_doc["games"]:
                if game["game"]["statusname"] == "Running":
                    games[str(game["game"]["id"])] = {
                        "name": game["game"]["name"],
                        "race": game["player"]["id"],
                    }
        return games
    logger.error("Failed to get running games from planets.nu.")
    raise typer.Exit()


def _mbox(game_id: str, api_key: str, race_id: str, outfile: Path) -> None:
    logger.info("Fetching messages for game %s.", game_id)
    messaging = Messaging(api_key)
    if planets["race_id"]:
        messages = messaging.get_messages_from_game(game_id, race_id)
    else:
        messages = messaging.get_all_messages_from_game(game_id)
    if messages:
        logger.info("Saving messages from game %s to %s.", game_id, outfile)
        exporting = Exporting()
        exporting.to_mbox(messages, outfile)
        logger.info("Messages saved.")
    else:
        logger.error("Could not get messages from game %s", game_id)
        raise typer.Exit()
