
import requests

BASE_URL = "http://127.0.0.1:8000"

cases = [
    ({"student_id": "22000001", "limit": 5}, 200),
    ({"student_id": "99999999"}, 200),
    ({"event_type": "CREATED", "limit": 10}, 200),
    ({"limit": 101}, 422),
    ({"skip": -1}, 422),
    ({"event_type": "INVALID"}, 400),
]

for params, expected_status in cases:
    response = requests.get(
        f"{BASE_URL}/enrollment-events",
        params=params,
        timeout=10,
    )

    print(params, response.status_code)
    assert response.status_code == expected_status

    if response.status_code == 200:
        assert isinstance(response.json(), list)

empty_response = requests.get(
    f"{BASE_URL}/enrollment-events",
    params={"student_id": "99999999"},
    timeout=10,
)
assert empty_response.json() == []

limited_response = requests.get(
    f"{BASE_URL}/enrollment-events",
    params={"student_id": "22000001", "limit": 5},
    timeout=10,
)
assert len(limited_response.json()) <= 5

print("PASS: Exercise XII - Bai 1")
