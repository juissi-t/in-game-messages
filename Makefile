IMAGE=in-game-messages
TAG=0.1.0
.DEFAULT_GOAL := install
.PHONY: install install-dev lint black test docker-build

install:  ## Install without dev dependencies
	pip install -U .

install-dev:  ## Install with dev dependencies
	pip install -U .\[dev]

lint:  ## Lint and static-check
	flake8 in_game_messages --exit-zero --max-line-length=88
	pylint in_game_messages --exit-zero
	mypy in_game_messages

black:  ## Format code
	black in_game_messages tests

test:  ## Run tests
	pytest

docker-build:  ## Build container
	docker build -t $(IMAGE):$(TAG) -f Dockerfile . ; \
