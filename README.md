# Planets.nu In-game Messaging

This project aims to provide some utilities to make it easier to consume [Planets Nu](https://planets.nu/) in-game messages in various formats.

## Installation

[Python](https://www.python.org/) version 3.7.9 or above is required.

To install the `in-game-messages` command line tool, clone this repository first. Then, if you have `make` installed, run `make install` in the repository directory. Else, run `pip install -U .`.

You may want to consider using a [virtualenv](https://virtualenv.pypa.io/en/latest/) for the tool instead of installing it globally.

## Usage

The tool can be used to send messages from a game to Slack, or to export them to a CSV or a mailbox file. Additionally, you can export messages from all of your running games to a mailbox file.

Running the tool always requires either your Planets Nu username and password, or your API key, to connect to the site API. The easiest way to use them is to export them as environment variables:

```console
% export PLANETS_API_KEY="xxxxxxxx-yyyy-zzzz-aaaa-bbbbbbbbbbbb"
# OR
% export PLANETS_USERNAME="<your username>"
% export PLANETS_PASSWORD="<your password>"
```

Alternatively, you can set the credentials as first options for the tool:

```console
% in-game-messages --planets-api-key="xxxxxxxx-yyyy-zzzz-aaaa-bbbbbbbbbbbb" <COMMAND>
# OR
% in-game-messages --planets-username="<your username>" --planets-password="<your password>" <COMMAND>
```

### Sending messages to Slack

To send messages to a Slack channel, you need to specify the game ID, race ID, Slack channel ID (channel name might work too, but is not guaranteed) and give a Slack bot token. Using environment variables:

```console
% export PLANETS_API_KEY="<your API key>"
% export PLANETS_GAME_ID="123456"
% export PLANETS_RACE_ID="7"
% export SLACK_BOT_TOKEN="<your Slack bot token>"
% export SLACK_CHANNEL_ID="<your Slack channel ID>"
% in-game-messages send slack
INFO:in_game_messages.cli:Fetching messages for game 123456.
INFO:in_game_messages.cli:Sending messages from game 123456 to Slack.
INFO:in_game_messages.slack_messaging:Message <5065809.0@123456.planets.nu> sent to Slack successfully.
INFO:in_game_messages.cli:Messages sent.
```

Using command line options:

```console
% in-game-messages send --planets-api-key="<your API key>" --planets-game-id="123456" --planets-race-id="7" slack --slack-bot-token="<your Slack bot token>" --slack-channel-id="<your Slack channel ID>"
INFO:in_game_messages.cli:Fetching messages for game 123456.
INFO:in_game_messages.cli:Sending messages from game 123456 to Slack.
INFO:in_game_messages.slack_messaging:Message <5065809.0@123456.planets.nu> sent to Slack successfully.
INFO:in_game_messages.cli:Messages sent.
```

Messages sent to Slack are stored in a mailbox file in the directory where the command is run. If you remove some messages from the mailbox (or the file), those messages will be re-sent to Slack when you run the command again.

#### Command line options and environment variables when sending messages to Slack

| Option | Environment variable | Explanation |
| ------ | -------------------- | ----------- |
| `--slack-bot-token` | `SLACK_BOT_TOKEN` | Bot token from your [Slack bot app](https://slack.com/intl/en-fi/help/articles/115005265703-Create-a-bot-for-your-workspace) which has the required permissions to post to your Slack workspace. |
| `--slack-channel-id` | `SLACK_CHANNEL_ID` | Slack channel ID or name. |
| `--planets-api-key` | `PLANETS_API_KEY` | Your Planets.Nu API key. Mutually exclusive with username and password. |
| `--planets-username` | `PLANETS_USERNAME` | Your Planets.Nu username. Password also required. |
| `--planets-password` | `PLANETS_PASSWORD` | Your Planets.Nu password. Username also required. |
| `--planets-game-id` | `PLANETS_GAME_ID` | Game ID for the game you want to fetch messages from. |
| `--planets-race-id` | `PLANETS_RACE_ID` | Race ID in the game to fet messages for. |

### Exporting messages to files

It's possible to export messages in either comma separated values (CSV) file or as a mailbox file. CSV file can be imported to a spreadsheet program for analysis, while mailbox can be imported to an e-mail client to read messages in a threaded view. To import the messages to [Thunderbird](https://www.thunderbird.net/), you can use the [ImportExportTools NG](https://addons.thunderbird.net/en-US/thunderbird/addon/importexporttools-ng/) add-on.

Similarly to sending messages to Slack, you can use either environment variables or command line options to specify your credentials and game settings. Using environment variables:

```console
% export PLANETS_API_KEY="<your API key>"
% export PLANETS_GAME_ID="123456"
% export PLANETS_RACE_ID="7"
# Export to a mailbox file
% in-game-messages export mbox 123456.mbox
INFO:in_game_messages.cli:Fetching messages for game 123456.
INFO:in_game_messages.cli:Saving messages from game 123456 to 123456.mbox.
INFO:in_game_messages.cli:Messages saved.
# Export to a CSV file
% in-game-messages export csv 123456.csv
INFO:in_game_messages.cli:Fetching messages for game 123456.
INFO:in_game_messages.cli:Saving messages from game 123456 to 123456.csv.
INFO:in_game_messages.cli:Messages saved.
```

To use command line options, please see the Slack example above.

#### Command line options and environment variables when exporting messages to files

| Option | Environment variable | Explanation |
| ------ | -------------------- | ----------- |
| `--planets-api-key` | `PLANETS_API_KEY` | Your Planets.Nu API key. Mutually exclusive with username and password. |
| `--planets-username` | `PLANETS_USERNAME` | Your Planets.Nu username. Password also required. |
| `--planets-password` | `PLANETS_PASSWORD` | Your Planets.Nu password. Username also required. |
| `--planets-game-id` | `PLANETS_GAME_ID` | Game ID for the game you want to fetch messages from. |
| `--planets-race-id` | `PLANETS_RACE_ID` | Race ID in the game to fet messages for. If undefined, fetch messages for all players in the game (works only for finished games). |

### Exporting messages for all running games to mailboxes

You can also fetch messages for all your running games. This might be useful in case you want to read the messages in your local e-mail client. As an argument to the command you need to supply a directory to hold the mailbox files. The directory must exist before running the command.

```console
% export PLANETS_API_KEY="<your API key>"
% in-game-messages export running-to-mbox games/
INFO:in_game_messages.cli:Getting list of active games.
INFO:in_game_messages.cli:Found games: 420232
INFO:in_game_messages.cli:Fetching messages for game 420232.
INFO:in_game_messages.cli:Saving messages from game 420232 to games/Tanascuis Sector (420232).
INFO:in_game_messages.cli:Messages saved.
```

To use command line options, please see the Slack example above.

#### Command line options and environment variables when exporting messages from running games

| Option | Environment variable | Explanation |
| ------ | -------------------- | ----------- |
| `--planets-api-key` | `PLANETS_API_KEY` | Your Planets.Nu API key. Mutually exclusive with username and password. |
| `--planets-username` | `PLANETS_USERNAME` | Your Planets.Nu username. Password also required. |
| `--planets-password` | `PLANETS_PASSWORD` | Your Planets.Nu password. Username also required. |

## Development

To install the required development tools ([Black](https://github.com/psf/black) for code formatting, [pytest](https://docs.pytest.org/en/stable/) for running tests, [pylint](https://www.pylint.org/), [flake8](https://flake8.pycqa.org/en/latest/) and [mypy](http://mypy-lang.org/) for static analysis), run `make install-dev`.

Run tests with `make test`. Make sure they all pass and you don't introduce any bugs in some parts of the codebase. Tests are in the `tests` subdirectory - please add more tests when you add some features.

```console
% make test
pytest
================================= test session starts ==================================
platform linux -- Python 3.8.6, pytest-6.2.0, py-1.10.0, pluggy-0.13.1
rootdir: /home/juissi/planets/in-game-messages
collected 14 items

tests/test_messaging.py ........                                                 [ 57%]
tests/test_slack_messaging.py ......                                             [100%]

================================== 14 passed in 0.10s ==================================
```

Code formatting is done by running `make black`. It will change the files to match the default Black formatting.

```console
% make black
black in_game_messages tests
All done! ✨ 🍰 ✨
8 files left unchanged.
```

Run static analysis tools with `make lint`. Ensure there are no errors and the code is rated 10.00, so that you don't accidentally introduce any complexities.

``` console
% make lint
flake8 in_game_messages --exit-zero --max-line-length=88
pylint in_game_messages --exit-zero

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

mypy in_game_messages
Success: no issues found in 4 source files
```

### Debugging

Use the `--debug` flag for the command to see more detailed output of what it is doing.

```console
% in-game-messages --debug export running-to-mbox games/
DEBUG:in_game_messages.cli:Debug logging enabled.
INFO:in_game_messages.cli:Getting list of active games.
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): api.planets.nu:443
DEBUG:urllib3.connectionpool:https://api.planets.nu:443 "POST /account/mygames HTTP/1.1" 200 6337
INFO:in_game_messages.cli:Found games: 420232
INFO:in_game_messages.cli:Fetching messages for game 420232.
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): api.planets.nu:443
DEBUG:urllib3.connectionpool:https://api.planets.nu:443 "POST /account/ingameactivity HTTP/1.1" 200 21848
INFO:in_game_messages.cli:Saving messages from game 420232 to games/Tanascuis Sector (420232).
DEBUG:in_game_messages.exporting:Writing messages to mbox games/Tanascuis Sector (420232)
DEBUG:in_game_messages.exporting:Wrote message <5166480.0@420232.planets.nu>
...
```

## Contributing

If you wish to share your new features and bug fixes, I'd be happy to receive them! Please fork this repository and create a [GitHub pull request](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-pull-requests) with your changes. I'll review the pull request and merge it once I'm happy with the contents.

## Future ideas

Here's an unordered list of future improvements to the project:

- Add some annotating [GitHub Actions](https://docs.github.com/en/free-pro-team@latest/actions) for `pytest`, `pylint`, `flake8` and `mypy` to ensure code quality with continuous integration and to automatically comment on pull requests when there are issues.
- Package the project as a Python package and publish in GitHub.
- Create a utility class for sending in-game messages.
- Move Planets.Nu API calls to their own class.
- More command-line commands for different purposes, e.g. sending messages to other messaging systems than Slack.
- Running the tool continuously for multiple games, sending messages to game-specific channels.
- Better comments, documenting the classes.

## License

[MIT](LICENSE)
