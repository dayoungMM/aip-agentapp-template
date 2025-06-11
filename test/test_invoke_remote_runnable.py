from langserve import RemoteRunnable
from langchain_core.runnables.config import RunnableConfig

def test_invoke_remote_runnable():
    
    headers = {
        "accept": "application/json",
        "aip-user": "aiplatform3/agenttest",
        "Authorization": "any-api-key",
        "Content-Type": "application/json",
    }

    agent = RemoteRunnable(
        "http://localhost:18080",
        headers=headers,
    )
    
    config = RunnableConfig(configurable={"system_prompt": "한국어로 대답해줘."})
    response = agent.invoke(
        {"messages": [{"content": "Hi", "type": "human"}]},
        config=config
    )
    print(response)
    assert response


if __name__ == "__main__":
    test_invoke_remote_runnable()
