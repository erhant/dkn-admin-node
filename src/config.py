import os


# Configuration class to encapsulate the environment variables
class Config:
    NODE_AUTH_KEY = os.getenv('NODE_AUTH_KEY', "default_auth_key")
    DRIA_PRIVATE_KEY = os.getenv('DRIA_PRIVATE_KEY', "")
    MONITORING_INTERVAL = 10
    POLLING_INTERVAL = 5
    INPUT_CONTENT_TOPIC = "/dria/2/synthesis/proto"
    TASK_TIMEOUT_MINUTE = 3
    COMPUTE_BY_JOB = 3
    DRIA_BASE_URL = os.getenv('DRIA_BASE_URL', "http://0.0.0.0:8002")


# Load the config once during startup or when needed
config = Config()
