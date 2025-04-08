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

## Launch langgraph server locally
```
sktaip-cli dev --host localhost --port 28080 --graph_yaml ./graph.yaml
```
## Build 

### 1. Build Automatically
> rename IMAGE_TAG for docker image tag. ex)react-agent-v0.1.0
```
sktaip-cli build -t IMAGE_TAG --graph_yaml ./graph.yaml
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

