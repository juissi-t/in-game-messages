# Planets.nu In-game Messaging

This project aims to provide some utilities to make it easier to consume [Planets Nu](https://planets.nu/) in-game messages in various formats.

## Installing the utilities

[Python](https://www.python.org/) version 3.8 or above is required.

To install the `in-game-messages` command line tool, clone this repository first. Then, if you have `make` installed, run `make install` in the repository directory. Else, run `pip install -U .`.

You may want to consider using a [virtualenv](https://virtualenv.pypa.io/en/latest/) for the tool instead of installing it globally.

## Running the command line utility to send messages to Slack

Run `in-game-messages` command with either some options or with some environment variables set.

```console
Usage: in-game-messages [OPTIONS]

  Send planets.nu in-game messages to Slack.

Options:
  --slack-bot-token TEXT   [required]
  --slack-channel-id TEXT  [required]
  --planets-api-key TEXT   [required]
  --planets-game-id TEXT   [required]
  --planets-race-id TEXT   [required]
  --debug
  --help                   Show this message and exit.
```

| Option | Environment variable | Explanation |
| ------ | -------------------- | ----------- |
| `--slack-bot-token` | `SLACK_BOT_TOKEN` | Bot token from your [Slack bot app](https://slack.com/intl/en-fi/help/articles/115005265703-Create-a-bot-for-your-workspace) which has the required permissions to post to your Slack workspace. |
| `--slack-channel-id` | `SLACK_CHANNEL_ID` | Slack channel ID or name. |
| `--planets-api-key` | `PLANETS_API_KEY` | API key from the game. |
| `--planets-game-id` | `PLANETS_GAME_ID` | Game ID for the game you want to fetch messages from. |
| `--planets-race-id` | `PLANETS_RACE_ID` | Race ID in the game to fet messages for. |

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

## Contributing

If you wish to share your new features and bug fixes, I'd be happy to receive them! Please fork this repository and create a [GitHub pull request](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-pull-requests) with your changes. I'll review the pull request and merge it once I'm happy with the contents.

## Future ideas

Here's an unordered list of future improvements to the project:

- Add some annotating [GitHub Actions](https://docs.github.com/en/free-pro-team@latest/actions) for `pytest`, `pylint`, `flake8` and `mypy` to ensure code quality with continuous integration and to automatically comment on pull requests when there are issues.
- Package the project as a Python package and publish in GitHub.
- Create a utility class for sending in-game messages.
- More command-line commands for different purposes, e.g. for downloading messages for a game in mbox format or sending to other messaging systems than Slack.
- Running the tool continuously for multiple games, sending messages to game-specific channels.
- Support for logging in to Planets Nu API instead of using API key directly.
- Refactor mailbox handling to its own class.
- Better comments, documenting the classes.
