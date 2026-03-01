export PYTHONPATH=./life-efficiency
AWS_REGION ?= eu-west-1
DEV_STACK ?= life-efficiency-dev
TELEGRAM_LOGICAL_ID ?= TelegramCheckFunction

lint:
	pipenv run python -m flake8

build:
	pipenv requirements > life-efficiency/requirements.txt
	pipenv run sam build -u

build-debug:
	pipenv requirements > life-efficiency/requirements.txt
	pipenv run sam build -u --debug

run: build
	cd local && docker-compose -f compose.yaml up -d
	pipenv run sam local start-api --docker-network life-efficiency --debug-port 1234 --skip-pull-image --warm-containers EAGER --docker-network life-efficiency --parameter-overrides ParameterKey=Environment,ParameterValue=local --container-env-vars local/local_env.json

invoke-telegram-check: build
	pipenv run sam local invoke TelegramCheckFunction --event events/telegram_schedule.json --env-vars local/telegram_env.json --parameter-overrides ParameterKey=Environment,ParameterValue=local

deploy-dev: build
	pipenv run sam deploy --no-confirm-changeset --region $(AWS_REGION) --stack-name $(DEV_STACK) --parameter-overrides ParameterKey=Environment,ParameterValue=Dev

deploy-prod: build
	pipenv run sam deploy --no-confirm-changeset --region $(AWS_REGION) --stack-name life-efficiency-prod --parameter-overrides ParameterKey=Environment,ParameterValue=Prod

telegram-logs-latest:
	@FUNC=$$(aws cloudformation describe-stack-resource --region $(AWS_REGION) --stack-name $(DEV_STACK) --logical-resource-id $(TELEGRAM_LOGICAL_ID) --query 'StackResourceDetail.PhysicalResourceId' --output text); \
	LOG_GROUP="/aws/lambda/$$FUNC"; \
	STREAM=$$(aws logs describe-log-streams --region $(AWS_REGION) --log-group-name "$$LOG_GROUP" --order-by LastEventTime --descending --max-items 1 --query 'logStreams[0].logStreamName' --output text); \
	aws logs get-log-events --region $(AWS_REGION) --log-group-name "$$LOG_GROUP" --log-stream-name "$$STREAM" --limit 200 --query 'events[-120:].[timestamp,message]' --output text

telegram-logs-tail:
	@FUNC=$$(aws cloudformation describe-stack-resource --region $(AWS_REGION) --stack-name $(DEV_STACK) --logical-resource-id $(TELEGRAM_LOGICAL_ID) --query 'StackResourceDetail.PhysicalResourceId' --output text); \
	aws logs tail "/aws/lambda/$$FUNC" --region $(AWS_REGION) --since 1h --follow

test:
	pipenv run python -m pytest --cov=life-efficiency ./tests

test-functional:
	pipenv run python -m pytest functional

debug-local-dynamo:
	docker run --network life-efficiency --rm -it --entrypoint /bin/sh amazon/aws-cli
	# export AWS_ACCESS_KEY_ID='a'; export AWS_SECRET_ACCESS_KEY='b'; aws dynamodb list-tables --endpoint-url http://localstack:4566 --region eu-west-1
