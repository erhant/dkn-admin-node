

import json
import requests


def health_check():
    response = requests.get("http://0.0.0.0:8646/health")
    return response.text == "Node is healthy"


def subscribe_topic(topic):

    response = requests.post(f"http://0.0.0.0:8646/relay/v1/subscriptions", data=json.dumps([topic]), headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        return True
    else:
        raise ValueError("Failed to subscribe topic")


def get_info():
    response = requests.get("http://0.0.0.0:8646/debug/v1/info")
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("Failed to get info")


def get_content_topic(content_topic):
    response = requests.get(f"http://0.0.0.0:8646/relay/v1/auto/messages/{content_topic}", headers={"Accept": "application/json"})
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("Failed to get content topic")


def push_content_topic(data, content_topic):
    response = requests.post(f"http://0.0.0.0:8646/relay/v1/auto/messages/{content_topic}", json=json.dumps(data))
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("Failed to push content topic")
