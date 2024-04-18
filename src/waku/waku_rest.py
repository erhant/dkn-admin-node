import json

import requests


class WakuClient:
    """
    Waku is a messaging protocol that allows for secure and private communication between nodes.

    This class provides a client to interact with the Waku node which builded with Compose.
    """
    def __init__(self):
        self.base_url = "http://0.0.0.0:8002"

    def health_check(self):
        """
        Perform a health check on the node.

        :return: True if the node is healthy, False otherwise.
        """
        response = requests.get(f"{self.base_url}/health")
        return response.text == "Node is healthy"

    def subscribe_topic(self, topic):
        """
        Subscribe to a topic.

        :param topic: The topic to subscribe to.
        :return: True if the subscription was successful, False otherwise.
        """

        response = requests.post(f"{self.base_url}/relay/v1/subscriptions",
                                 data=json.dumps([topic]),
                                 headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            return True
        else:
            raise ValueError("Failed to subscribe topic")

    def get_info(self):
        """
        Information about the status of Waku.

        :return: The status of Waku.
        """
        response = requests.get(f"{self.base_url}/debug/v1/info")
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError("Failed to get info")

    def get_content_topic(self, content_topic):
        """
        Get content topic.

        :param content_topic: The content topic to get.
        :return: Messages from the content topic.
        """
        response = requests.get(f"{self.base_url}/relay/v1/auto/messages/{content_topic}",
                                headers={"Accept": "application/json"})
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError("Failed to get content topic")

    def push_content_topic(self, data, content_topic):
        response = requests.post(f"{self.base_url}/relay/v1/auto/messages/{content_topic}", json=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError("Failed to push content topic")
