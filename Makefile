export PYTHONPATH=./life-efficiency

lint:
	pipenv run python -m flake8

build:
	pipenv requirements > life-efficiency/requirements.txt
	sam build -u

run:
	docker-compose -f compose.yaml up -d
	sam local start-api --docker-network life-efficiency --debug-port 1234 --skip-pull-image --warm-containers EAGER --docker-network life-efficiency --parameter-overrides ParameterKey=Environment,ParameterValue=local --container-env-vars local_env.json

deploy-dev:
	sam deploy --no-confirm-changeset --region eu-west-1 --stack-name life-efficiency-dev --parameter-overrides ParameterKey=Environment,ParameterValue=Dev

deploy-prod: build
	sam deploy --no-confirm-changeset --region eu-west-1 --stack-name life-efficiency-prod --parameter-overrides ParameterKey=Environment,ParameterValue=Prod

test:
	pipenv run python -m pytest --cov=life-efficiency ./tests

test-functional:
	pipenv run python -m pytest functional

debug-local-dynamo:
	docker run --network life-efficiency --rm -it --entrypoint /bin/sh amazon/aws-cli
	# export AWS_ACCESS_KEY_ID='a'; export AWS_SECRET_ACCESS_KEY='b'; aws dynamodb list-tables --endpoint-url http://dynamodb:8000 --region eu-west-1
