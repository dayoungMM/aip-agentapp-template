import requests
import datetime
import pytest


def test_invoke_api():
    url = "http://localhost:28080/invoke"
    headers = {
        "accept": "application/json",
        "aip-user": "aiplatform3/agenttest",
        "Authorization": "sk-525b3af2fc709905407c63e47bab36b7",
        "Content-Type": "application/json",
    }

    # 현재 시스템 시간을 system_prompt에 반영합니다.
    system_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "input": {"messages": [{"content": "how are you?", "type": "human"}]},
        "config": {
            "configurable": {
                "max_search_results": 10,
                "system_prompt": f"You are a helpful AI assistant.\n\nSystem time: {system_time}",
            }
        },
        "kwargs": {},
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Response status code:", response.status_code)
    print("Response body:", response.text)

    # 상태 코드가 200임을 검증합니다.
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    # 응답이 JSON 형식인지 확인합니다.
    try:
        json_response = response.json()
    except Exception as e:
        pytest.fail("Response is not valid JSON")

    # 응답 JSON에 예상되는 키가 포함되어 있는지 확인할 수 있습니다.
    # (예시로 "result" 또는 "output"이 포함되었는지 검증)
    assert (
        "result" in json_response or "output" in json_response
    ), "Response JSON does not contain expected key"


if __name__ == "__main__":
    test_invoke_api()
