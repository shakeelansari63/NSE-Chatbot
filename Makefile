.PHONY: run setup

.DEFAULT_GOAL := run

run:
	uv run main.py

setup:
	uv sync
