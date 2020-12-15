# -*- coding: utf-8 -*-
"""Cli interface for sending in-game messages to Slack."""

import logging

import click

from in_game_messages.messaging import Messaging, SlackMessaging


@click.command()
@click.option("--slack-bot-token", type=str, envvar="SLACK_BOT_TOKEN", required=True)
@click.option("--slack-channel-id", type=str, envvar="SLACK_CHANNEL_ID", required=True)
@click.option("--planets-api-key", type=str, envvar="PLANETS_API_KEY", required=True)
@click.option("--planets-game-id", type=str, envvar="PLANETS_GAME_ID", required=True)
@click.option("--planets-race-id", type=str, envvar="PLANETS_RACE_ID", required=True)
@click.option("--debug", default=False, is_flag=True)
# pylint: disable=too-many-arguments
def main(
    slack_bot_token: str,
    slack_channel_id: str,
    planets_api_key: str,
    planets_game_id: str,
    planets_race_id: str,
    debug: bool,
):
    """Main method for starting up the messages to Slack process."""
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
