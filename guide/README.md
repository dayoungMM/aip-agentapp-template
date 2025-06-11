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