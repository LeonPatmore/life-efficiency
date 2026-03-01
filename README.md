# Life Efficiency

[![<LeonPatmore>](https://circleci.com/gh/LeonPatmore/life-efficiency.svg?style=shield)](<LINK>)


A project to improve the efficiency of my life!

## Running Locally

### Running Tests

We are using pytest to test this project, and a pytest plugin to monitor the test coverage.

`make test`

### Running the Linter

We are using flake8 as our super cool Python linter.

`make lint`

### Building

`make build`

### Running Lambda Locally

`make run`

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/sam.ps1` | Runs SAM CLI via a Python 3.12 venv. Use when `pipenv run sam` fails (e.g. on Python 3.14). |
| `scripts/build-deploy-dev.ps1` | Clean build and deploy to dev: removes `.aws-sam`, regenerates requirements.txt (UTF-8), runs `sam build -u`, deploys. Use instead of `make deploy-dev` on Windows. |

## Deploying

### SAM CLI on Python 3.14

If your local environment uses Python 3.14, `pipenv run sam ...` can fail due to upstream SAM CLI
dependency compatibility. Use the repo script below instead; it bootstraps a dedicated SAM CLI venv
on Python 3.12:

`powershell -ExecutionPolicy Bypass -File scripts/sam.ps1 --version`

Examples:

`powershell -ExecutionPolicy Bypass -File scripts/sam.ps1 build -u`

`powershell -ExecutionPolicy Bypass -File scripts/sam.ps1 deploy --no-confirm-changeset --region eu-west-1 --stack-name life-efficiency-dev --parameter-overrides ParameterKey=Environment,ParameterValue=Dev`

### Dev

`make deploy-dev`

### Prod

`make deploy-prod`

## Functional Tests

`make test-functional`

Use the `ENV` environment variable to test against local or dev instance. Valid values are `dev` and `local`.

## TODO

https://github.com/todotxt/todo.txt

## Shopping

### History

Shopping history is stored.
