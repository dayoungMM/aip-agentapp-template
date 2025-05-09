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
pip install adxp-cli
```
2. requirements.txt 사용하는 경우
```
pip install -r requirements.txt
```

## Launch langgraph server locally
```
adxp-cli agent run --host localhost --port 28080 --graph_yaml ./graph.yaml
```
## Build 

### 1. Build Automatically
> rename IMAGE_NAME for docker image
```
adxp-cli agent build -t IMAGE_NAME  --graph_yaml ./graph.yaml
```

### 2. Build Via Dockerfile
2.1 Create Dockerfile
```
adxp-cli agent dockerfile --output ./sktaip.Dockerfile --graph_yaml ./graph.yaml
```
2.2 Docker build
```
docker build -t IMAGE_NAME -f ./sktaip.Dockerfile .
```

## How to Request to Server
1. API 

> Please add the user's question to the `messages` field in the `input`.

![Swagger UI](./static/swagger.png)

```bash
curl -X 'POST' \
  'http://localhost:28080/invoke' \
  -H 'aip-user: <any user name>' \
  -H 'secret-mode: false' \
  -H 'Authorization: <your api key>' \
  -H 'Content-Type: application/json' \
  -d '{
  "input": {
    "messages": [
            {
                "content": "kiiikiii가 누구야??",
                "type": "human"
            }]
  }
}'
```

2. Python

```python
from langserve import RemoteRunnable

headers = {
    "aip-user": "<any user name",
    "Authorization": "<your api key></your>",
}

agent = RemoteRunnable(
    "http://localhost:28080",
    headers=headers,
)
response = agent.invoke(
    {"messages": [{"content": "Hi", "type": "human"}]}
)
print(response)
assert response

```

3. Playground
3.1 Login Page
> http://localhost:28080/login \
`api_key` and `user_name` is required

![Login UI](./static/playground_login.png)

3.2 Playground

> Run Graph via Playground. Add user Question at Input Message Form

![Run UI](./static/playground_run.png)