import json
from typing import List, Union

import requests

from src.config import Config
from .errors import HollowDBError


class HollowClient:
    """
    A client for interacting with the HollowDB database.
    """

    def __init__(self):
        """
        Initialize the HollowClient with the configuration.
        """
        self.config = Config()
        self.__BASE_URL = self.config.HOLLOWDB_URL

    def get_multi(self, keys: List[str], contract_id: str) -> List[Union[str, dict]]:
        """
        Get multiple values corresponding to a list of keys.

        Args:
            keys (List[str]): A list of keys to fetch values for.
            contract_id (str): The ID of the contract.

        Returns:
            List[Union[str, dict]]: A list of values corresponding to the provided keys.

        Raises:
            HollowDBError: If there is no data at the specified keys.
        """
        keys_data = json.dumps({"keys": keys, "contractTxId": contract_id}, separators=(",", ":"))
        response = self._fetch(f"{self.__BASE_URL}/mget", "POST", keys_data)

        if "data" not in response:
            raise HollowDBError("No data at this key", "")

        return response["data"]["result"]

    def get(self, key: str) -> Union[str, dict]:
        """
        Get the value corresponding to a single key.

        Args:
            key (str): The key to fetch the value for.

        Returns:
            Union[str, dict]: The value corresponding to the provided key.

        Raises:
            HollowDBError: If there is no data at the specified key.
        """
        encoded_key = requests.utils.quote(key)
        response = self._fetch(f"{self.__BASE_URL}/get/{encoded_key}", "GET")

        if "data" not in response:
            raise HollowDBError("No data at this key", "")

        return response["data"]["result"]

    def push_contract(self, key: str, value: Union[str, dict]):
        """
        Push a new value to an existing key in the contract.

        Args:
            key (str): The key to push the value to.
            value (Union[str, dict]): The value to push.
        """
        encoded_key = requests.utils.quote(key)
        response = self._fetch(f"{self.__BASE_URL}/get/{encoded_key}", "GET")

        contract_list = response["data"]["result"] if "data" in response else []
        contract_list = contract_list if contract_list is not None else []

        contract_list.append(value)

        options = {"expire": None, "blockchain": "none"}
        body = json.dumps({"key": key, "value": contract_list, "options": options})
        self._put_or_update(f"{self.__BASE_URL}/put", body)

    def put(self, key: str, value: Union[str, dict]):
        """
        Put a new key-value pair in the database.

        Args:
            key (str): The key to put the value under.
            value (Union[str, dict]): The value to put.
        """
        options = {"expire": None, "blockchain": "none"}
        body = json.dumps({"key": key, "value": value, "options": options})
        self._put_or_update(f"{self.__BASE_URL}/put", body)

    def update_key(self, key: str, field: str, value: str):
        """
        Update a field in an existing key-value pair.

        Args:
            key (str): The key to update.
            field (str): The field to update.
            value (str): The new value for the field.
        """
        encoded_key = requests.utils.quote(key)
        response = self._fetch(f"{self.__BASE_URL}/get/{encoded_key}", "GET")

        if "data" not in response:
            raise HollowDBError("No data at this key", "")

        options = {"expire": None, "blockchain": "none"}
        data = response["data"]["result"]
        data[field] = value
        body = json.dumps({"key": key, "value": data, "options": options})
        self._put_or_update(f"{self.__BASE_URL}/update", body)

    def _put_or_update(self, url: str, body: str):
        """
        Helper method to perform a PUT or UPDATE request based on the response.

        Args:
            url (str): The URL to send the request to.
            body (str): The request body as a JSON string.
        """
        try:
            self._fetch(url, "POST", body)
        except HollowDBError:
            self._fetch(f"{self.__BASE_URL}/update", "POST", body)

    def _fetch(self, url: str, method: str, body: str = None) -> Union[dict, None]:
        """
        Helper method to send a request to the HollowDB API.

        Args:
            url (str): The URL to send the request to.
            method (str): The HTTP method to use (GET, POST).
            body (str, optional): The request body as a JSON string (for POST requests).

        Returns:
            Union[dict, None]: The response JSON data or None if an error occurred.

        Raises:
            ValueError: If an invalid HTTP method is provided.
            HollowDBError: If the request fails with a non-200 status code.
        """
        headers = {
            "Content-Type": "application/json",
            "x-secret-key": self.config.HOLLOWDB_SECRET_KEY,
        }

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=body)
        else:
            raise ValueError("Invalid method")

        response_json = response.json()

        if response.status_code == 200:
            if "newBearer" in response_json:
                self.__auth_token = response_json["newBearer"]
            return response_json
        else:
            raise HollowDBError(
                f"{url}: Status: {response.status_code} Error: {response_json['message']}",
                "",
            )
