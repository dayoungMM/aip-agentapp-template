# aip-agentapp-template
AIX Platform의 CLI로 배포하는 Agent APP Template

## Prerequisite
- python >= 3.10
- docker
- pydantic >=2.10.0,<2.11.0

## create env
create env file
```
cp .env.example .env
```
Please fill in appropriate values

## Installation
1. requirements.txt 가 없는 경우
```
pip install sktaip-cli
```
2. requirements.txt 사용하는 경우
```
pip install -r requirements.txt
```

## Create template (Unsupported)
> You can git clone this repository instead of aip-cli new
```
sktaip-cli new [PATH] --template default
```

## Launch langgraph server locally
```
sktaip-cli dev --host localhost --port 28080 --graph_yaml ./graph.yaml
```
## Build 

### 1. Build Automatically
> rename IMAGE_TAG for docker image tag. ex)react-agent-v0.1.0
```
sktaip-cli build -t IMAGE_TAG --./langgraph.json
```

### 2. Build Via Dockerfile
2.1 Create Dockerfile
```
sktaip-cli dockerfile --output ./sktaip.Dockerfile --graph_yaml ./graph.yaml
```
2.2 Docker build
```
docker build -t IMAGE_TAG -f ./sktaip.Dockerfile .
```

## Push docker image (Not Available)
```
sktaip-cli push -t IMAGE_TAG 
```
## Deploy New App to Platform (Not Available)
```
sktaip-cli login --endpoint https://aip.sktai.io
sktaip-cli deploy -t IMAGE_TAG_V1 -model MODEL_1 -model MODEL_2 -n MY_APP_NAME -desc MY_APP_DESC
sktaip-cli get-app --id MY_APP_ID
sktaip-cli create-apikey --app_id MY_APP_ID
sktaip-cli get-apikey --app_id MY_APP_ID
sktaip-cli invoke-example
```
## Deploy New Version to Exsiting APP (Not Available)
```
sktaip-cli deploy -id MY_APP_ID -t IMAGE_TAG_V2 -model MODEL_1 -model MODEL_2 -n MY_VERSION_NAME -desc MY_VERSION_DESC
```

## Generate langgraph dockerfile (Not Available)
```
sktaip-cli dockerfile
```