# -*- coding: utf-8 -*-
"""Cli interface for sending in-game messages to Slack."""

import logging

import click

from in_game_messages.messaging import SlackMessaging


@click.command()
@click.option("--slack-bot-token", type=str, envvar="SLACK_BOT_TOKEN")
@click.option("--slack-channel-id", type=str, envvar="SLACK_CHANNEL_ID")
@click.option("--planets-api-key", type=str, envvar="PLANETS_API_KEY")
@click.option("--planets-game-id", type=str, envvar="PLANETS_GAME_ID")
@click.option("--planets-race-id", type=str, envvar="PLANETS_RACE_ID")
@click.option("--debug", default=False, is_flag=True)
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

    logging.info("Sending messages from game %s to Slack.", planets_game_id)
    messaging = SlackMessaging(
        slack_bot_token,
        slack_channel_id,
        planets_api_key,
        planets_game_id,
        planets_race_id,
    )
    messaging.send_new_messages_to_slack()
    logging.info("Messages sent.")
