build:
	sam build -u

run:
	sam local start-api --warm-containers EAGER
