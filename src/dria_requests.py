import logging

import requests

from src.config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DriaClient:
    """
    DRIA client to handle requests to the DRIA API.

    Dria API is a service that provides a RESTful API for managing tasks and nodes in a decentralized network.

    Attributes:
        base_url (str): Base URL for the DRIA API.
        session (requests.Session): Session object for connection pooling.

    """

    def __init__(self):
        self.base_url = config.dria_base_url
        logging.basicConfig(level=logging.INFO)
        self.session = requests.Session()  # Using session for connection pooling

    def _make_request(self, method, endpoint, data=None):
        """Helper method to handle requests"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.lower() == 'get':
                response = self.session.get(url)
            elif method.lower() == 'post':
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check if the request was successful
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            logging.error(f"HTTP error occurred: {e} - {response.status_code} - {response.text}")
            raise
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            raise
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise

    def add_available_nodes(self, nodes):
        """Add available nodes to the database"""
        return self._make_request('post', '/nodes/add', data=nodes)

    def fetch_tasks(self):
        """Fetch all tasks"""
        tasks = self._make_request('get', '/tasks/publisher')
        task_status, task_data = tasks.get("success", False), tasks.get("data", [])
        if task_status:
            return task_data
        logging.warning(task_data["message"])
        return []

    def fetch_aggregation_tasks(self):
        """Fetch aggregation tasks"""
        return self._make_request('get', '/tasks/aggregation')
