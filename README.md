# Life Efficiency

[![<LeonPatmore>](https://circleci.com/gh/LeonPatmore/life-efficiency.svg?style=shield)](<LINK>)


A project to improve the efficiency of my life!

## Running Locally

All commands should be ran from the root of the repo.

1. Make sure that you set your python path to the source root (this is different from the repo root):

    **Windows**:

    `set PYTHONPATH=%PYTHONPATH%;.\life-efficiency`

2. Make sure your AWS credentials are setup:

    **Windows**:

    `set AWS_CONFIG_FILE=D:\Tools\cygwin\home\Leon\.aws\config`

    `set AWS_SHARED_CREDENTIALS_FILE=D:\Tools\cygwin\home\Leon\.aws\credentials`

2. `pipenv install -d`

3. `pipenv run python life-efficiency/main.py`

### Running Tests

We are using pytest to test this project, and a pytest plugin to monitor the test coverage.

`pipenv run python -m pytest --cov=life-efficiency`

### Running the Linter

We are using flake8 as our super cool Python linter.

`pipenv run python -m flake8`

## Building

1. Update the requirements file: `pipenv lock -r > life-efficiency/requirements.txt`.

2. Build `sam build -u`

## Running Lambda Locally

`sam local start-api`

## Deploying

### Dev

`sam deploy --stack-name life-efficiency-dev`

### Prod

`sam deploy --stack-name life-efficiency-prod --parameter-overrides ParameterKey=Environment,ParameterValue=Prod`

## Functional Tests

Note: You must have valid AWS environment setup.

`pipenv run python -m pytest functional`

## TODO
https://github.com/todotxt/todo.txt

## Shopping

### History

Shopping history is stored.
