build:
	sam build -u

run:
	sam local start-api --warm-containers EAGER

deploy-prod:
	sam deploy --region eu-west-1 --stack-name life-efficiency-prod --parameter-overrides ParameterKey=Environment,ParameterValue=Prod
