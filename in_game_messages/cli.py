# -*- coding: utf-8 -*-
"""Cli interface for sending in-game messages to Slack."""

import logging

import typer

from in_game_messages.messaging import Messaging
from in_game_messages.slack_messaging import SlackMessaging

app = typer.Typer()


@app.command()
# pylint: disable=too-many-arguments
def main(
    slack_bot_token: str = typer.Option(..., envvar="SLACK_BOT_TOKEN"),
    slack_channel_id: str = typer.Option(..., envvar="SLACK_CHANNEL_ID"),
    planets_api_key: str = typer.Option(..., envvar="PLANETS_API_KEY"),
    planets_game_id: str = typer.Option(..., envvar="PLANETS_GAME_ID"),
    planets_race_id: str = typer.Option(..., envvar="PLANETS_RACE_ID"),
    debug: bool = False,
):
    """Send planets.nu in-game messages to Slack."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.info("Fetching messages for game %s.", planets_game_id)
    messaging = Messaging(planets_api_key)
    messages = messaging.get_messages_from_game(planets_game_id, planets_race_id)
    if messages:
        logging.info("Sending messages from game %s to Slack.", planets_game_id)
        slack_messaging = SlackMessaging(
            slack_bot_token,
            slack_channel_id,
        )
        slack_messaging.send_new_messages_to_slack(messages, planets_game_id)
        logging.info("Messages sent.")
    else:
        logging.error("Could not get messages from game %s", planets_game_id)
