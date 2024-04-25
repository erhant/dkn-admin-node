import json
import logging
import urllib.parse
from typing import Dict, List, Union

import requests
from requests.adapters import HTTPAdapter, Retry

from src.config import config
from src.exceptions import WakuSubscriptionError, WakuClientError, WakuContentTopicError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)


class WakuClient:
    """
    Waku is a messaging protocol that allows for secure and private communication between nodes.

    This class provides a client to interact with the Waku node which is built with Compose.
    """

    def __init__(self, base_url: str = config.WAKU_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def health_check(self) -> bool:
        """
        Perform a health check on the node.

        :return: True if the node is healthy, False otherwise.
        """
        response = self.session.get(f"{self.base_url}/health")
        return response.text == "Node is healthy"

    def subscribe_topic(self, topic: str) -> bool:
        """
        Subscribe to a topic.

        :param topic: The topic to subscribe to.
        :return: True if the subscription was successful, False otherwise.
        :raises WakuSubscriptionError: If there is an error subscribing to the topic.
        """
        try:
            response = self.session.post(f"{self.base_url}/relay/v1/subscriptions",
                                         data=json.dumps([f"{urllib.parse.quote_plus(topic)}"]),
                                         headers={"Content-Type": "application/json"})
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to subscribe to topic {topic}: {e}")
            raise WakuSubscriptionError(f"Failed to subscribe to topic {topic}") from e

    def get_info(self) -> Dict:
        """
        Information about the status of Waku.

        :return: The status of Waku.
        :raises WakuClientError: If there is an error getting the Waku info.
        """
        try:
            response = self.session.get(f"{self.base_url}/debug/v1/info")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Waku info: {e}")
            raise WakuClientError("Failed to get Waku info") from e

    def get_content_topic(self, content_topic: str) -> List[Dict]:
        """
        Get content topic.

        :param content_topic: The content topic to get.
        :return: Messages from the content topic.
        :raises WakuContentTopicError: If there is an error getting the content topic.
        """
        try:
            response = self.session.get(
                f"{self.base_url}/relay/v1/auto/messages/{urllib.parse.quote_plus(content_topic)}",
                headers={"Accept": "application/json"})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get content topic {content_topic}: {e}")
            raise WakuContentTopicError(f"Failed to get content topic {content_topic}") from e

    def push_content_topic(self, data: Union[str, bytes], content_topic: str) -> str:
        """
        Push content to a topic.

        :param data: The data to push.
        :param content_topic: The content topic to push to.
        :return: A success message.
        :raises WakuContentTopicError: If there is an error pushing the content topic.
        """
        try:
            response = self.session.post(f"{self.base_url}/relay/v1/auto/messages",
                                         json={"payload": data,
                                               "contentTopic": content_topic},
                                         headers={"Content-Type": "application/json"})
            if response.status_code == 404:
                self.subscribe_topic(content_topic)
                response = self.session.post(f"{self.base_url}/relay/v1/auto/messages",
                                             json={"payload": data,
                                                   "contentTopic": content_topic},
                                             headers={"Content-Type": "application/json"})
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to push content topic {content_topic}: {e}")
            raise WakuContentTopicError(f"Failed to push content topic {content_topic}") from e
