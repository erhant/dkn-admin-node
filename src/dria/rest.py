import logging
from typing import Dict, List, Union

import requests

from src.utils.task_utils import resolve_tasks

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DriaClient:
    """
    DRIA client to handle requests to the DRIA API.

    Dria API is a service that provides a RESTful API for managing tasks and nodes in a decentralized network.

    Attributes:
        base_url (str): Base URL for the DRIA API.
        session (requests.Session): Session object for connection pooling.

    """

    def __init__(self, config):
        self.base_url = config.dria_base_url
        logging.basicConfig(level=logging.INFO)
        self.session = requests.Session()  # Using session for connection pooling

    def _make_request(self, method: str, endpoint: str, data: Union[dict, list] = None) -> Union[dict, list]:
        """
        Helper method to handle requests.

        :param method: HTTP method to use (GET, POST, etc.)
        :param endpoint: API endpoint to call
        :param data: Data to send in the request (if applicable)
        :return: Response data from the API
        :raises ValueError: If the HTTP method is not supported
        :raises requests.HTTPError: If the API request fails
        :raises requests.RequestException: If there's a general issue with the request
        :raises Exception: If any other unexpected error occurs
        """
        url = f"{self.base_url}{endpoint}"
        try:
            if method.lower() == "get":
                response = self.session.get(url)
            elif method.lower() == "post":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check if the request was successful
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            logging.error(
                f"HTTP error occurred: {e} - {response.status_code} - {response.text}"
            )
            raise
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            raise
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise

    def add_available_nodes(self, nodes: Union[dict, list]) -> Union[dict, list]:
        """
        Add available nodes to the database.

        :param nodes: List or dictionary of nodes to add
        :return: Response data from the API
        :raises requests.HTTPError: If the API request fails
        :raises requests.RequestException: If there's a general issue with the request
        :raises Exception: If any other unexpected error occurs
        """
        return self._make_request("post", "/nodes/add", data=nodes)

    def fetch_tasks(self):
        """
        Fetch all tasks.

        :return: List of tasks
        :raises requests.HTTPError: If the API request fails
        :raises requests.RequestException: If there's a general issue with the request
        :raises Exception: If any other unexpected error occurs
        """
        try:
            tasks = self._make_request("get", "/tasks/publisher")
            task_status, task_data = tasks.get("success", False), tasks.get("data", [])
            if task_status:
                return task_data["tasks"]
            logging.warning(task_data.get("message", "No tasks found"))
            return []
        except (ValueError, TypeError) as e:
            logging.error(f"Error resolving tasks: {e}")
            return []

    def fetch_aggregation_tasks(self) -> Union[dict, list]:
        """
        Fetch aggregation tasks.

        :return: Response data from the API
        :raises requests.HTTPError: If the API request fails
        :raises requests.RequestException: If there's a general issue with the request
        :raises Exception: If any other unexpected error occurs
        """
        return self._make_request("get", "/tasks/aggregation")
