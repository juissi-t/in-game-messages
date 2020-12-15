IMAGE=in-game-messages
TAG=0.1.0
.DEFAULT_GOAL := help
.PHONY: deps lint test

deps:  ## Install dependencies
	pip install -U .\[dev]

lint:  ## Lint and static-check
	flake8 in_game_messages --exit-zero --max-line-length=88
	pylint in_game_messages --exit-zero
	mypy in_game_messages

black:
	black in_game_messages

test:  ## Run tests
	pytest

docker-build:
	docker build -t $(IMAGE):$(TAG) -f Dockerfile . ; \
