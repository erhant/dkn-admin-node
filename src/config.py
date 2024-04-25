import os


# Configuration class to encapsulate the environment variables
class Config:
    NODE_AUTH_KEY = os.getenv('NODE_AUTH_KEY', "default_auth_key")
    DRIA_PRIVATE_KEY = os.getenv('DRIA_PRIVATE_KEY', "6472696164726961647269616472696164726961647269616472696164726961")
    AGGREGATOR_WORKERS = os.getenv('AGGREGATOR_WORKERS', 1)
    WAKU_BASE_URL = os.getenv('WAKU_BASE_URL', "http://127.0.0.0:8645")
    PUBLISHER_WORKERS = os.getenv('PUBLISHER_WORKERS', 1)
    MONITORING_WORKERS = os.getenv('MONITORING_WORKERS', 1)
    MONITORING_INTERVAL = 10
    POLLING_INTERVAL = 5
    INPUT_CONTENT_TOPIC = "/dria/0/synth/proto"
    TASK_TIMEOUT_MINUTE = 3
    COMPUTE_BY_JOB = 3
    DRIA_BASE_URL = os.getenv('DRIA_BASE_URL', "http://0.0.0.0:8002")


# Load the config once during startup or when needed
config = Config()
