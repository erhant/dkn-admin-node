import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.node_auth_key: str = self._get_env_var("NODE_AUTH_KEY", "default_auth_key")
        self.dria_private_key: str = self._get_env_var(
            "DRIA_PRIVATE_KEY",
            self._get_env_var("DRIA_PRIVATE_KEY", "dria_private_key"),
        )
        self.aggregator_workers: int = self._get_env_var("AGGREGATOR_WORKERS", 1, int)
        self.waku_base_url: str = self._get_env_var(
            "WAKU_BASE_URL", "http://127.0.0.1:8645"
        )
        self.publisher_workers: int = self._get_env_var("PUBLISHER_WORKERS", 1, int)
        self.monitoring_workers: int = self._get_env_var("MONITORING_WORKERS", 1, int)
        self.monitoring_interval: int = 10
        self.polling_interval: int = 5
        self.input_content_topic: str = "/dria/0/synthesis/proto"
        self.heartbeat_topic: str = "/dria/0/heartbeat/proto"
        self.task_timeout_minute: int = 3
        self.compute_by_job: int = 3
        self.dria_base_url: str = self._get_env_var(
            "DRIA_BASE_URL", "http://0.0.0.0:8005"
        )

    @staticmethod
    def _get_env_var(
            key: str, default_value: Any = None, value_type: type = str
    ) -> Any:
        """
        Retrieves an environment variable value from the system.

        Args:
            key (str): The name of the environment variable.
            default_value (Any): The default value to return if the environment variable is not set.
            value_type (type): The expected type of the environment variable value.

        Returns:
            Any: The value of the environment variable, or the default value if not set.

        Raises:
            ValueError: If the environment variable value cannot be converted to the expected type.
        """
        try:
            value = os.getenv(key, default_value)
            if value is not None and value_type != str:
                value = value_type(value)
            return value
        except ValueError as e:
            logger.error(f"Error getting environment variable {key}: {e}", exc_info=True)
            raise ValueError(f"Invalid value for {key}: {e}") from e
        except Exception as e:
            logger.error(f"Error getting environment variable {key}: {e}", exc_info=True)
            raise e


# Load the config once during startup or when needed
config = Config()
