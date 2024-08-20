test:
	poetry run pytest

lint:
	poetry run flake8

install:
	poetry install

build:
	./build.sh

test-build:
	./test_build.sh

dev:
	poetry run flask --app page_analyzer:app --debug run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app



.PHONY: test lint install build
