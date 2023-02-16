FROM python:3.10.10-slim-bullseye

WORKDIR /build
COPY in_game_messages ./in_game_messages/
COPY setup.py .
RUN pip install -U .

# Cleanup
WORKDIR /
RUN rm -rf /build

WORKDIR /in-game-messages

CMD [ "in-game-messages" ]
