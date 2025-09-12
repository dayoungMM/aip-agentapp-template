# LangGraph 코드 개발 가이드

## 1. graph.py는 LangGraph의 CompiledStateGraph를 만드는 파일입니다.
> 참고: `simple_graph/graph.py`, `custom_stream/graph.py`

```python
# Define a new graph
builder = StateGraph(State, input=InputState, config_schema=BaseConfiguration)

builder.add_node(call_model)


builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)


graph = builder.compile(
    interrupt_before=[],  # Add node names here to update state before they're called
    interrupt_after=[],  # Add node names here to update state after they're called
)
graph.name = "Simple Graph"  # This customizes the name in LangSmith
```

## 2. InputState에 따라 API Request Body가 결정됩니다.
> 참고: `simple_graph/state.py`

### 2.2 State 선언부
```python
@dataclass
class InputState:
    """Defines the input state for the agent, representing a narrower interface to the outside world.

    This class is used to define the initial state and structure of incoming data.
    """

    messages: Sequence[AnyMessage] = field(
        default_factory=list
    )
    """
```
### 2.3 Request Body 
```shell
curl --location 'http://localhost:18080/invoke' \
--header 'authorization: <any-key>' \
--header 'aip-user: <username>' \
--header 'Content-Type: application/json' \
--data '{
  "input": {
        "messages": [
            {
                "content": "kiiikiii가 누구야?? Hi My name is Sam",
                "type": "human"
            }]
        
  }
}'
```
Request in Python 
```python
def test_invoke_remote_runnable():
    
    headers = {
        "accept": "application/json",
        "aip-user": "<your username>",
        "Authorization": "<any-api-key>",
        "Content-Type": "application/json",
    }

    agent = RemoteRunnable(
        "http://localhost:18080",
        headers=headers,
    )
    
    response = agent.invoke(
        {"messages": [{"content": "Hi", "type": "human"}]},
    )
    print(response)
    assert response
```

## 3. Request Body에 input 외에 config를 넣고싶은 경우
> 참고: `custom_stream/configuration.py`, `custom_stream/graph.py`

### 3.1 StateGraph 선언시 config_schema를 명시해주세요.
명시를 해주시면 FastAPI router 만들 때 body에서 config를 받을 수 있게 세팅을 합니다. 아래는 config_schema 예시입니다

```python
builder = StateGraph(State, input=InputState, config_schema=BodyConfiguration)

builder.add_node(call_model)


builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)


graph = builder.compile()
```

```python
    
class BodyConfiguration(BaseModel):
    system_prompt: str = Field(
        default=prompts.SYSTEM_PROMPT,
        description="The system prompt to use for the agent's interactions. "
    )
    llm_provider: str | None = Field(default="oai")

```

###  3.2 Remote Runnable로 요청
```python
from langserve import RemoteRunnable
from langchain_core.runnables.config import RunnableConfig

def test_invoke_remote_runnable():
    
    headers = {
        "accept": "application/json",
        "aip-user": "<your username>",
        "Authorization": "<any-api-key>",
        "Content-Type": "application/json",
    }

    agent = RemoteRunnable(
        "http://localhost:18080",
        headers=headers,
    )
    
    config = RunnableConfig(configurable={"llm_provider": "oai"})
    response = agent.invoke(
        {"messages": [{"content": "Hi", "type": "human"}]},
        config=config
    )
    print(response)
    assert response
```

### 3.3 Node 안에서 config 를 받을 수 있습니다.
> 참고: `custom_stream/graph.py`

```

async def call_model(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    llm_provider = config.get("configurable", {}).get("llm_provider")
    
```

## 4. Header에서 값을 받아 LangGraph의 Node에서 사용하고 싶은 경우
> `config["configurable"]["aip_headers"]` 를 파싱해서 사용하세요

> 참고: `custom_stream/graph.py`

```python
from adxp_sdk.serves.utils import AIPHeaders

async def call_model(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    
    configuration = HeaderMergedConfig.model_validate(config.get("configurable", {}))

    # If you want to use the AIP headers, get them from the Runnable Config
    # AIP headers are used to logging in A.X Platform Gateway. If you don't want to use them, you can remove this part.
    if isinstance(configuration.aip_headers, dict):
        aip_headers: AIPHeaders = AIPHeaders.model_validate(configuration.aip_headers)
    elif isinstance(configuration.aip_headers, AIPHeaders):
        aip_headers = configuration.aip_headers
    else:
        raise ValueError(f"Invalid aip_headers type: {type(configuration.aip_headers)}")

    headers = aip_headers.get_headers_without_authorization()    
    api_key = aip_headers.authorization
    
    llm = ChatOpenAI(
        api_key=SecretStr(api_key),
        base_url=os.getenv("AIP_MODEL_ENDPOINT"),
        model=os.getenv("AIP_MODEL"),
        default_headers=headers,
    )
```

## 5. Stream 가능한 Graph 생성하기
- LanGraph의 stream 기능을 지원합니다.[더 알아보기]( https://langchain-ai.github.io/langgraph/how-tos/streaming/#supported-stream-modes)

| 모드 | 설명 |
| --- | --- |
| `values` | 그래프의 각 단계 이후 상태(state)의 전체 값을 스트리밍합니다. |
| `updates` | 그래프의 각 단계 이후 상태에 대한 업데이트만을 스트리밍합니다. 한 단계에서 여러 업데이트가 발생할 경우(예: 여러 노드 실행), 각각의 업데이트가 별도로 스트리밍됩니다. |
| `custom` | 그래프 노드 내부에서 정의된 사용자 정의 데이터를 스트리밍합니다. |
| `messages` | LLM이 호출되는 그래프 노드에서 `(LLM 토큰, 메타데이터)` 형태의 2-튜플을 스트리밍합니다. |
| `debug` | 그래프 실행 중 가능한 모든 정보를 스트리밍합니다. |

- LangGraph에서 제공하는 Stream Writer를 이용하면 Stream 데이터를 커스텀할 수 있습니다.

```python
from typing import TypedDict
from langgraph.config import get_stream_writer
from langgraph.graph import StateGraph, START

class State(TypedDict):
    query: str
    answer: str

def node(state: State):
    writer = get_stream_writer()  
    writer({"custom_key": "Generating custom data inside node"}) 
    return {"answer": "some data"}

graph = (
    StateGraph(State)
    .add_node(node)
    .add_edge(START, "node")
    .compile()
)

inputs = {"query": "example"}

# Usage
for chunk in graph.stream(inputs, stream_mode="custom"):  
    print(chunk)
```

- graph.yaml에서 stream_mode를 설정해주세요
```yaml
package_directory: .
graph_path: ./custom_stream/graph.py:graph
env_file: .env
requirements_file: ./requirements.txt
stream_mode: custom
```