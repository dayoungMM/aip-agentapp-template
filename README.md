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
1. CLI 설치 (0.1.5 이상의 버전을 사용하세요)
```
pip install adxp-cli
```
2. requirements.txt 사용하는 경우
```
pip install -r requirements.txt
```

## Launch langgraph server locally
### 1. In Terminal
```
adxp-cli agent run --host localhost --port 18080 --graph_yaml ./graph.yaml
```
### 2. Launch in Visual Studio
Click Launcher 
- adxp-cli run (single): run with graph.yaml
- adxp-cli run (multiple): run with graph-multiple.yaml
![Vscode_launcher](./static/vscode_launcher.png)

### 3. Launch with python
```
python -m adxp_cli.cli agent run --host 127.0.0.1 --port 18080 --graph_yaml ./graph.yaml
```

### 4. Edit graph.yaml
> graph.yaml (Default. Single Agent) 
- package_directory
  - Specifies the root directory of the Python package to reference when running the agent
  - Example: . (current directory)
- graph_path
  - Specifies the location of the graph object to actually use
  - Format: python_file_path:object_path
  - Example: ./simple_graph/graph.py:graph
    → Uses the graph object from simple_graph/graph.py file
- env_file
  - Specifies the path to the environment variable file (.env) to load when running the agent
  - Example: .env
- requirements_file
  - Specifies the path to the requirements.txt file containing the list of required Python packages
  - Example: ./requirements.txt

```yaml
package_directory: .
graph_path: ./simple_graph/graph.py:graph
env_file: .env
requirements_file: ./requirements.txt
```
The following APIs are created when launched
- http://localhost:28080/invoke
- http://localhost:28080/stream
- http://localhost:28080/batch

> graph-multiple.yaml (For multiple agents configuration)

This feature is supported only in adxp-cli version 0.1.6 or higher. change graph_path to **list** format

- graph_path
  - Multiple graph objects can be specified in list format
  - Each graph object has a name and object_path
    - name: Unique identifier for the graph
    - object_path: Actual location of the graph object (python_file_path:object_path)
  - In the example, 2 graph objects are created from the same graph.py file with names 'first' and 'second'

```yaml
package_directory: .
graph_path: 
  - name: first
    object_path: ./simple_graph/graph.py:graph
  - name: second
    object_path: ./simple_graph/graph.py:graph
env_file: .env
requirements_file: ./requirements.txt
```
The following APIs are created when launched
- http://localhost:28080/first/invoke
- http://localhost:28080/first/stream
- http://localhost:28080/first/batch
- http://localhost:28080/second/invoke
- http://localhost:28080/second/stream
- http://localhost:28080/second/batch



> graph-stream.yaml (To Use LangGraph Stream Mode)

This feature is supported only in adxp-cli version 0.1.7 or higher. Set `stream_mode`

If you want to know about LangGraph stream mode, See this page
-   https://langchain-ai.github.io/langgraph/how-tos/streaming/#supported-stream-modes


Supported Stream Mode
| Mode | Description |
| --- | --- |
| values | Streams the full value of the state after each step of the graph. |
| updates | Streams the updates to the state after each step of the graph. If multiple updates are made in the same step (e.g., multiple nodes are run), those updates are streamed separately. |
| custom | Streams custom data from inside your graph nodes. |
| messages | Streams 2-tuples (LLM token, metadata) from any graph nodes where an LLM is invoked. |
| debug | Streams as much information as possible throughout the execution of the graph. |

```yaml
package_directory: .
graph_path: ./custom_stream/graph.py:graph
env_file: .env
requirements_file: ./requirements.txt
stream_mode: custom
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
## 3. Run docker image on local
```
docker run -d -p 18080:18080 IMAGE_NAME
```
## 서버에 요청하는 방법
1. API 

> 이 API는 효율적인 /invoke, /batch 및 /stream 엔드포인트를 제공하여 단일 서버에서 많은 동시 요청을 처리할 수 있습니다.

![Swagger UI](./static/swagger.png)

### API 엔드포인트

#### 1. POST /invoke
- **Description**: 단일 입력에 대해 실행 가능한 작업을 호출합니다.
> **AIP RequestBody**

| key | type | description |
| --- | --- | --- |
| input | Object | Graph의 State의 schema를 따름.  (예: `simple_graph/state.py의 InputState`) |
| config | json | LangChain의 RunnableConfig.  |

> **AIP RequestHeader**

All endpoints require specific headers for authentication and request identification.
| Header Name | Required | Description |
|-------------------------|----------|-----------------------------------------------------------------------------|
| aip-user | Yes | User ID. |
| Authorization | Yes | API Key. For local testing, use a dummy value. On the platform, obtain the API Key from the web UI. |
| aip-app-serving-id | No | Container identifier used internally by the platform. |
| aip-transaction-id | No | Value to identify the request. |
| aip-company | No | Company name. |
| aip-department | No | Department name. |
| aip-chat-id | No | Value to identify the conversation. |
Note:
- aip-user and Authorization are required for all requests.
- For **local development**, you may use **any dummy value** for **Authorization**.
- On the deployed platform, you can find your API Key in the web interface. 

> **AIP ResponseBody**

| key | type | description |
| --- | --- | --- |
| output | Object | Graph의 State의 schema를 따름.  (예: `simple_graph/state.py의 InputState`) |
| metadata | json | Graph 실행의 metadata.  |

> Example

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


#### 2. POST /stream
- **Description**: 단일 입력에 대해 실행 가능한 작업을 호출하고 출력을 스트리밍합니다.
> **AIP RequestBody**

| key | type | description |
| --- | --- | --- |
| input | Object | Graph의 State의 schema를 따름.  (예: `simple_graph/state.py의 InputState`) |
| config | json | LangChain의 RunnableConfig.  |

> **AIP RequestHeader**

All endpoints require specific headers for authentication and request identification.
| Header Name | Required | Description |
|-------------------------|----------|-----------------------------------------------------------------------------|
| aip-user | Yes | User ID. |
| Authorization | Yes | API Key. For local testing, use a dummy value. On the platform, obtain the API Key from the web UI. |
| aip-app-serving-id | No | Container identifier used internally by the platform. |
| aip-transaction-id | No | Value to identify the request. |
| aip-company | No | Company name. |
| aip-department | No | Department name. |
| aip-chat-id | No | Value to identify the conversation. |
Note:
- aip-user and Authorization are required for all requests.
- For **local development**, you may use **any dummy value** for **Authorization**.
- On the deployed platform, you can find your API Key in the web interface. 

> **AIP ResponseBody**

The /stream endpoint returns a Server-Sent Events (SSE) stream.
Each event contains information about the execution of nodes in the graph.
**Event Types**
- metadata
  - Contains metadata about the run (e.g., run_id).
- data
  - Contains the output of a node in the graph.
- end
  - Indicates the end of the stream.

> Example

request
```bash
curl -X 'POST' \
  'http://localhost:28080/stream' \
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

response
```
event: metadata
data: {"run_id": "<unique-run-id>"}

event: data
data: {
  "<node_id>": <node_output>
}

event: end

```



#### 3. POST /batch  
- **Description**: 여러 입력에 대해 일괄적으로 실행 가능한 작업을 호출합니다.
> **AIP RequestBody**

| key | type | description |
| --- | --- | --- |
| inputs | list[Object] | Graph의 State의 schema를 따름.  (예: `simple_graph/state.py의 InputState`) |
| config | json | LangChain의 RunnableConfig.  |

> **AIP RequestHeader**

All endpoints require specific headers for authentication and request identification.
| Header Name | Required | Description |
|-------------------------|----------|-----------------------------------------------------------------------------|
| aip-user | Yes | User ID. |
| Authorization | Yes | API Key. For local testing, use a dummy value. On the platform, obtain the API Key from the web UI. |
| aip-app-serving-id | No | Container identifier used internally by the platform. |
| aip-transaction-id | No | Value to identify the request. |
| aip-company | No | Company name. |
| aip-department | No | Department name. |
| aip-chat-id | No | Value to identify the conversation. |
Note:
- aip-user and Authorization are required for all requests.
- For **local development**, you may use **any dummy value** for **Authorization**.
- On the deployed platform, you can find your API Key in the web interface. 

> **AIP ResponseBody**

| key | type | description |
| --- | --- | --- |
| output | Object | Graph의 State의 schema를 따름.  (예: `simple_graph/state.py의 InputState`) |
| metadata | json | Graph 실행의 metadata.  |

> Example

```bash
curl --location 'http://localhost:18080/batch' \
--header 'authorization: <your api key>' \
--header 'aip-user: <any user name>' \
--header 'Content-Type: application/json' \
--data '{
    "inputs": [
        {
            "messages": [
                {
                    "content": "kiiikiii가 누구야??",
                    "type": "human"
                }
            ]
        },
        {
            "messages": [
                {
                    "content": "IVE가  누구야??",
                    "type": "human"
                }
            ]
        }
    ]
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