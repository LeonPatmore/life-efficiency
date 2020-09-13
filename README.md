# Life Efficiency

A project to improve the efficiency of my life!

## Running Locally

All commands should be ran from the root of the repo.

1. Make sure that you set your python path to the source root (this is different from the repo root):

    **Windows**:

    `set PYTHONPATH=%PYTHONPATH%;.\life-efficiency`

2. `pipenv install -d`

3. `pipenv run python life-efficiency/main.py`

### Running Tests

We are using pytest to test this project, and a pytest plugin to monitor the test coverage.

`pipenv run python -m pytest --cov=life-efficiency`

### Running the Linter

We are using flake8 as our super cool Python linter.

`pipenv run python -m flake8`

## TODO
https://github.com/todotxt/todo.txt

## Shopping

### History

Shopping history is stored.

### Predicting Shopping Needs

