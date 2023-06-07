export PYTHONPATH=./life-efficiency

build:
	sam build -u

run:
	sam local start-api --warm-containers EAGER

deploy-dev:
	sam deploy --no-confirm-changeset --region eu-west-1 --stack-name life-efficiency-dev

deploy-prod:
	sam deploy --no-confirm-changeset --region eu-west-1 --stack-name life-efficiency-prod --parameter-overrides ParameterKey=Environment,ParameterValue=Prod

test:
	pipenv run python -m pytest --cov=life-efficiency ./tests
