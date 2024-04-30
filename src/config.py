import os
from typing import Optional


class Config:
    def __init__(self):
        self.node_auth_key: str = self._get_env_var("NODE_AUTH_KEY", "default_auth_key")
        self.dria_private_key: str = self._get_env_var(
            "DRIA_PRIVATE_KEY",
            "6472696164726961647269616472696164726961647269616472696164726961",
        )
        self.aggregator_workers: int = self._get_env_var("AGGREGATOR_WORKERS", 1, int)
        self.waku_base_url: str = self._get_env_var(
            "WAKU_BASE_URL", "http://127.0.0.1:8645"
        )
        self.publisher_workers: str = self._get_env_var("PUBLISHER_WORKERS", 1, int)
        self.monitoring_workers: int = self._get_env_var("MONITORING_WORKERS", 1, int)
        self.monitoring_interval: int = 10
        self.polling_interval: int = 5
        self.input_content_topic: str = "/dria/0/synth/proto"
        self.heartbeat_topic: str = "/dria/0/heartbeat/proto"
        self.task_timeout_minute: int = 3
        self.compute_by_job: int = 3
        self.dria_base_url: str = self._get_env_var(
            "DRIA_BASE_URL", "http://0.0.0.0:8006"
        )

    @staticmethod
    def _get_env_var(
        key: str, default_value: Optional[str] = None, value_type: type = str
    ):
        """
        Retrieves an environment variable value from the system.

        Args:
            key (str): The name of the environment variable.
            default_value (Optional[str]): The default value to return if the environment variable is not set.
            value_type (type): The expected type of the environment variable value.

        Returns:
            Optional[str]: The value of the environment variable, or the default value if not set.
        """
        value = os.getenv(key, default_value)
        if value is not None and value_type != str:
            try:
                value = value_type(value)
            except ValueError:
                raise ValueError(f"Invalid value for {key}: {value}")
        return value


# Load the config once during startup or when needed
config = Config()
