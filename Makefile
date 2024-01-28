export PYTHONPATH=./life-efficiency

lint:
	pipenv run python -m flake8

build:
	sam build -u

run:
	docker-compose -f compose.yaml up -d
	sam local start-api --docker-network life-efficiency --debug-port 1234 --skip-pull-image --warm-containers EAGER --docker-network life-efficiency --parameter-overrides ParameterKey=Environment,ParameterValue=Local --container-env-vars local_env.json

deploy-dev:
	sam deploy --no-confirm-changeset --region eu-west-1 --stack-name life-efficiency-dev --parameter-overrides ParameterKey=Environment,ParameterValue=Dev

deploy-prod: build
	sam deploy --no-confirm-changeset --region eu-west-1 --stack-name life-efficiency-prod --parameter-overrides ParameterKey=Environment,ParameterValue=Prod

test:
	pipenv run python -m pytest --cov=life-efficiency ./tests

test-functional:
	pipenv run python -m pytest functional
