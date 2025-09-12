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
1. CLI 설치 (0.1.10 이상의 버전을 사용하세요)
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

This feature is supported only in adxp-cli version 0.1.10 or higher. Set `stream_mode`

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

## A.X Platform에 배포하기
### Login/Logout to Platform

#### 1. Login to A.X Platform(필수)

```
$ adxp-cli auth login
username: your_id
password:  # Input is hidden for security
project: your_project
base_url [<https://aip.sktai.io>]:  # Press Enter to use default value

Login successful. Authentication information has been saved.

```

#### 2. Refresh Token
- Token expires in 2 days. You can refresh your token using the following command:

```
$adxp-cli auth refresh
Enter your password to refresh the token.
password: # Input is hidden for security

Token has been successfully refreshed.

```

#### 4. Logout

```
$adxp-cli auth logout

Authentication information has been successfully deleted.

```

### Deploy New App to Platform

#### 1. Create New App(필수)

> 1개의 Agent APP은 N개의 Deployment(Version) 을 가집니다.
> 

```python
$ adxp-cli agent deploy --help
Usage: cli.py agent deploy [OPTIONS]

  Deploy Agent App to A.X Platform

Options:
  -t, --image TEXT                Image Tag. Example:
                                  https://myregistry.azurecr.io/myrepo/sample-
                                  app:v0.0.1  [required]
  -m, --model TEXT                Model
  -n, --name TEXT                 Name  [required]
  -d, --description TEXT          Description
  -e, --env-path TEXT             Path to .env file
  -i, --app-id TEXT               App ID
  --cpu-request INTEGER           cpu resource
  --cpu-limit INTEGER             cpu resource limit
  --mem-request INTEGER           memory resource
  --mem-limit INTEGER             memory resource limit
  --min-replicas INTEGER          minimum replicas
  --max-replicas INTEGER          maximum replicas
  --workers-per-core INTEGER      workers per core(cpu)
  --use-external-registry / --no-external-registry
                                  사용자 registry 사용 / 플랫폼 registry 사용
  -y, --skip-confirm              Automatically answer 'yes' to all
                                  confirmation prompts.                             
  --help                          Show this message and exit.
```

> 플랫폼 registry 사용할 경우
    
    ```python
    $adxp-cli agent deploy --image aip-harbor.sktai.io/sktai/agent/app:moondy-simple-v6 --name MY_APP_NAME --description MY_DESCRIPTION --env-path MY_PRD_ENV_PATH --no-external-registry
    
    ```
    

> 사용자 registry 사용할 경우

```
$adxp-cli agent deploy --image myharbor/myregistry:IMAGE_TAG --name MY_APP_NAME --description MY_DESCRIPTION --env-path MY_PRD_ENV_PATH --use-external-registry

Do you want to push the image(myharbor/myregistry:IMAGE_TAG) to docker registry? [Y/n]: y
(y로 할 경우 docker push 가 실행되고, n으로 할경우 docker push를 패스합니다.)
+ docker push aip-harbor.sktai.io/sktai/agent/app:moondy-simple-v6
... 중략
✅ Docker push completed
🐳 Image: myharbor/myregistry:IMAGE_TAG

You have selected to use your own registry.(use_external_registry: True)
Note: Registry secret must be pre-registered on the platform when using private registry.
Do you want to proceed? [y/N]: y

✅ Successfully deployed agent app.
🚀 에이전트 배포 결과

|--------------|---------------------------------------------------------------------------|
| Status       | Deploying                                                                 |
| App ID       | APP_ID                                                                    |
| Version      | 1                                                                         |
| Deployment ID| DEPLOYMENT ID (This is ID for Version)                                    |
| Endpoint     | <https://aip.sktai.io/api/v1/agent_gateway/APP_ID>                        |
| Description  | MY_DESCRIPTION                                                            |
| Created By   | XXXX                                                                      |
| Created At   | 2025-06-04T09:47:31.280336                                                |

🧩 리소스 정보
... CPU, MEMORY
🔑 모델 리스트
... model list ...

⚙️ Agent ENV
... env 정보 ...

✅ Deployment started successfully.
Deployment Status: Deploying
Endpoint: <https://aip.sktai.io/api/v1/agent_gateway/APP_ID>

🔑 API Key
API Key: ...

```

> [참고]model list 를 argument로 주는 경우
    
    model_list 가 필요한 경우는 다음과 같습니다. 이 경우가 아니라면 parameter를 무시하셔도 됩니다. (default: None)
    
    - aip_headers에서 api key를 받아서, 그 키를  A.X Model Gateway 호출시 api-key로서 사용하는 경우에만 model_list가 필요합니다.
    - 모델 배포시 api key가 자동으로 생성되는데, A.X Model Gateway의 권한도 같이 부여하기 위한 파라미터입니다.
    
    이 경우에 해당되지 않는다면 model이 필요하지 않습니다.
    
    aip_headers가 뭔지 모른다면, model이 필요하지 않는다는 것입니다. 
    
    model(list) 가 필요한 경우는 다음과 같이 option을 넣어주세요
    
    ```bash
    $adxp-cli agent deploy --image myharbor/myregistry:IMAGE_TAG --model MODEL_1,MODEL2 --name MY_APP_NAME --description MY_DESCRIPTION --env-path MY_PRD_ENV_PATH
    ```
    
#### 2. Update App

```
adxp-cli agent update --app-id MY_APP_ID --description "new" --name "new_name"
```

#### 3. Delete App

```
adxp-cli agent delete --app-id MY_APP_ID
```

### Get Deployed Agent Information

#### 1. List of Deployed Agent in your project (필수)

```
$adxp-cli agent ls

✅ Deployed Custom Agent APPs:
|    | id                                   | name                  | versions   |
|----|--------------------------------------|-----------------------|------------|
|  0 | e7b4166a-21d9-4894-8c05-cdfdb48xxxxx | interpretation agent  | 1          |
|  1 | 77f4d031-aafa-4317-9738-469d824xxxxx | interpretation agent2 | 1          |
|  2 | 20842586-f721-4a5c-9be2-92363ebxxxxx | moondy-simple-agent   | 1, 2       |

# If you want to see more columns, execute with -a option
$adxp-cli agent ls -a

```

#### 2. Get Detail Information of Deployed Agent (-a : show all versions of app) (필수)

```
adxp-cli agent get -i MY_APP_ID
adxp-cli agent get -i MY_APP_ID -a  (-a 옵션이 있나요? 동작하지 않음. 25.06.24)

```

### APP Deployment CRUD

#### 1. Deploy New Version to Exsiting APP (Add Deployment)

> 1개의 Agent APP은 N개의 Deployment(Version) 을 가집니다. 이미 존재하는 APP에 Deployment(Version)을 추가하는 방법입니다.
> 

```
$adxp-cli agent deploy --app-id MY_APP_ID --image myharbor/myregistry:IMAGE_TAG --model MODEL_1,MODEL2 --name MY_APP_NAME --description MY_DESCRIPTION --env-path MY_PRD_ENV_PATH

✅ Successfully deployed agent app.
🚀 에이전트 배포 결과
...

🧩 리소스 정보
...

🔑 모델 리스트
...
⚙️ Agent ENV
...                                                                           |

✅ Deployment started successfully.
Deployment Status: Deploying
Endpoint: ...

🔑 API Key
API Key: ...

```

#### 2. Stop Deployment(Version) (필수)

<aside>
💡 사용하지 않거나, 최신이 아닌 버전은 꼭 stop 하거나 delete해주세요. 자원이 한정적이니 협조 부탁드립니다.

</aside>

```
adxp-cli agent stop --deployment-id MY_DEPLOYMENT_ID

```

#### 3. Restart Deployment(Version) (필수)

```
adxp-cli agent restart --deployment-id MY_DEPLOYMENT_ID

```

#### 4. Delete Deployment(Version)

```
adxp-cli agent delete --deployment-id MY_DEPLOYMENT_ID

```

### API KEY CRUD

#### 1. ApiKey CRUD

<aside>
💡 App이나 Deployment를 배포할 경우 api key는 자동으로 생성 및 업데이트 됩니다. 추가적인 api key가 필요하거나 업데이트가 필요한 경우에만 아래의 명령어를 사용하세요.

</aside>

##### Create Additional Api Key for Deployed Agent

```
adxp-cli agent create-apikey -i MY_APP_ID

```

##### Regenerate Api Key for Deployed Agent

> APIKEY_NUMBER: Number of Api Key to Regenerate. (Default: 1) 
Check APIKEY_NUMBER by execute cli :  `$adxp-cli agent get -i <app_id>`
> 

```
adxp-cli agent regen-apikey -i MY_APP_ID -n APIKEY_NUMBER

```

##### Delete Api Key

```
adxp-cli agent rm-apikey -i MY_APP_ID -n APIKEY_NUMBER

```


## PAAS custom agent 용 가이드
- PAAS시스템은 뉴로 환경 내 서비스 앱 내에서만 접근 가능하므로 로컬 서버 테스트 불가.
- 로직이 구현된 graph_paas.py파일의 권한을 수정(chmod 666 custom_stream/graph_paas.py)하여 이미지 반입 후 vi(vim)모드로 수정해가며 디버깅해야함.
1. git clone 후 .env파일 생성 및 환경에 맟게 PAAS_PRD_ENDPOINT 또는 PAAS_STG_ENDPOINT 정의
   ```yaml
    PAAS_PRD_ENDPOINT=http://61.250.32.73:31000/pe/chat-completions/stream
    PAAS_STG_ENDPOINT=http://61.250.32.73:32000/pe/chat-completions/stream
   ```

2. graph_paas.py 작업
3. graph-paas-stream.yaml 작업
> graph-paas-stream.yaml  
- package_directory
  - Specifies the root directory of the Python package to reference when running the paas custom agent
  - Example: . (current directory)
- graph_path
  - Specifies the location of the graph object to actually use
  - Format: python_file_path:object_path
  - Example: ./custom_stream/graph_paas.py:runnable
- env_file
  - make env file with end point of PAASS
  - Example: .env
- requirements_file
  - Specifies the path to the requirements.txt file containing the list of required Python packages
  - Example: ./requirements_paas.txt

```yaml
package_directory: .
graph_path: ./custom_stream/graph_paas.py:runnable
env_file: .env
requirements_file: ./requirements_paas.txt
stream_mode: custom
```

4. sktaip.Dockerfile 파일 루트 경로에 생성
   ```yaml
    ARG PLATFORM_ARCH="linux/amd64"
    FROM --platform=${PLATFORM_ARCH} python:3.10-bookworm
    ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
    ENV PYTHONUNBUFFERED=1
    RUN apt-get update && \
        apt-get install -y vim curl yq jq
    RUN addgroup -gid 1000 usergroup && \
        adduser user \
        --disabled-password \
        -u 1000 --gecos "" \
        --ingroup 0 \
        --ingroup usergroup && \
        mkdir -p /workdir && \
        chown -R user:usergroup /workdir
    WORKDIR /workdir
    USER user
    ENV HOME=/home/user
    ENV PATH="${HOME}/.local/bin:${PATH}"
    ENV WORKER_CLASS="uvicorn.workers.UvicornWorker"
    ENV APP__HOST=0.0.0.0
    ENV APP__PORT=18080
    ENV LOG_LEVEL=info
    ENV GRACEFUL_TIMEOUT=600
    ENV TIMEOUT=600
    ENV KEEP_ALIVE=600
    # For distinguishing between deployed app and agent-backend
    ENV IS_DEPLOYED_APP=true
    ADD . /workdir/.
    RUN python -m pip install adxp-sdk
    RUN python -m pip install -r ./requirements_paas.txt
    RUN echo 'import os' > /workdir/server.py && \
        echo 'from adxp_sdk.serves.server import get_server' >> /workdir/server.py && \
        echo '' >> /workdir/server.py && \
        echo 'app = get_server("./custom_stream/graph_paas.py:runnable", ".env" , "custom")' >> /workdir/server.py
    ENV APP_MODULE="server:app"
    EXPOSE 18080
    SHELL ["/bin/sh", "-c"]
    CMD python -m uvicorn ${APP_MODULE} \
        --host ${APP__HOST} \
        --port ${APP__PORT} \
        --reload \
        --log-level ${LOG_LEVEL}
   ```

5. 로컬에서 이미지 빌드 및 푸쉬
- docker build --no-cache -f sktaip.Dockerfile --platform=linux/amd64 -t aip-harbor.sktai.io/sktai/agent/app:custom-agent-paas-v1.7-prd .
- docker push --platform=linux/amd64 aip-harbor.sktai.io/sktai/agent/app:custom-agent-paas-v1.7-prd

6. 뉴로 환경으로 이미지 반입
- 분당 개발기 하버-> ACR -> 뉴로 개발/스테이징/운영

7. 반입 이미지 적용
- 해당 프로젝트 inferenceService의 image 태그 변경(변경 시 자동으로 파드 재시작 됨.)

8. 테스트
- Agent gateway swagger 접속 후, id, apikey입력 후 stream 요청
![Vscode_launcher](./static/paas_neuro_gateway_swagger.png)

- 파드 로그 확인
![Vscode_launcher](./static/paas_neuro_pod_log.png)
