export PYTHONPATH=./life-efficiency

lint:
	pipenv run python -m flake8

build:
	sam build -u

run:
	docker-compose -f compose.yaml up -d
	sam local start-api --skip-pull-image --warm-containers EAGER --docker-network life-efficiency

deploy-dev:
	sam deploy --no-confirm-changeset --region eu-west-1 --stack-name life-efficiency-dev

deploy-prod:
	sam deploy --no-confirm-changeset --region eu-west-1 --stack-name life-efficiency-prod --parameter-overrides ParameterKey=Environment,ParameterValue=Prod

test:
	pipenv run python -m pytest --cov=life-efficiency ./tests

test-functional:
	pipenv run python -m pytest functional
