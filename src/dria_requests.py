import logging

import requests

from src.config import config


class DriaClient:
    """
    DRIA client to handle requests to the DRIA API.

    Dria API is a service that provides a RESTful API for managing tasks and nodes in a decentralized network.

    Attributes:
        auth (str): Authentication token for the DRIA API.
        base_url (str): Base URL for the DRIA API.
        headers (dict): Headers to be included in the request.
        session (requests.Session): Session object for connection pooling.

    """

    def __init__(self, auth):
        self.auth = auth
        self.base_url = config.DRIA_BASE_URL
        self.headers = {"Authorization": f"Bearer {self.auth}"}
        logging.basicConfig(level=logging.INFO)
        self.session = requests.Session()  # Using session for connection pooling

    def _make_request(self, method, endpoint, data=None):
        """Helper method to handle requests"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.lower() == 'get':
                response = self.session.get(url, headers=self.headers)
            elif method.lower() == 'post':
                response = self.session.post(url, headers=self.headers, json=data)
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
        return self._make_request('get', '/tasks/publisher')

    def fetch_aggregation_tasks(self):
        """Fetch aggregation tasks"""
        return self._make_request('get', '/tasks/aggregation')
