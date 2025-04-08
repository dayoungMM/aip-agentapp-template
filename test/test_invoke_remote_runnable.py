import requests
import datetime
import pytest
from langserve import RemoteRunnable


def test_invoke_remote_runnable():
    
    headers = {
        "accept": "application/json",
        "aip-user": "aiplatform3/agenttest",
        "Authorization": "sk-525b3af2fc709905407c63e47bab36b7",
        "Content-Type": "application/json",
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


if __name__ == "__main__":
    test_invoke_remote_runnable()
