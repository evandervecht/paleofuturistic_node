#!/bin/sh
: ; exec uv run --group dev python _CI/tasks.py "$@"
@uv run --group dev python _CI\tasks.py %*
