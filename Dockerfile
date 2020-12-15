FROM python:3.8.6-slim-buster

WORKDIR /build
COPY in_game_messages ./in_game_messages/
COPY setup.py .
RUN pip install -U .

# Cleanup
WORKDIR /
RUN rm -rf /build

CMD [ "in-game-messages" ]
