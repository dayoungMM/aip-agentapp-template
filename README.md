# aip-agentapp-template
AIX Platform의 CLI로 배포하는 Agent APP Template

## Prerequisite
- python >= 3.10

## create env
create env file
```
cp .env.example .env
```
Please fill in appropriate values

## Installation
pip install aip-cli
pip install -r requirements.txt

## Create template
> You can git clone this repository instead of aip-cli new
aip-cli new [PATH] --template default

vi .env

## Launch langgraph server locally
aip-cli dev --host localhost --port 18082 -c ./langgraph.json

## Build docker image
aip-cli build -t IMAGE_TAG --platform lunux/amd64 -c ./aix-platform.json

## Generate langgraph dockerfile
aip-cli dockerfile

## Dockercompose up (with opensearch)
aip-cli up --port 18082 -c ./aix-platform.json