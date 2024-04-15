import logging
import time

from dria_nodes.src.dria_requests import DriaClient
from dria_nodes.src.utils.rsa import generate_keys
from dria_nodes.src.waku.waku_rest import push_content_topic, get_content_topic

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Read configuration from environment or config file
from dria_nodes.src.config import DRIA_AUTH_KEY, POLLING_INTERVAL


def main():
    # Initialize Dria client with secret auth key
    try:
        dria_client = DriaClient(auth=DRIA_AUTH_KEY)
        logging.info("DRIA Client initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize DRIA Client: {e}")
        return

    # Check job availability and handle accordingly
    try:
        is_available = dria_client.is_available()
        logging.info(f"Job availability checked: {is_available}")

        if is_available:
            # Handling available jobs
            push_content_topic({"type": "available_node"}, "request")
            while True:
                time.sleep(POLLING_INTERVAL)
                available_nodes = get_content_topic("request")
                if available_nodes:
                    logging.info(f"Available nodes: {available_nodes}")
                    break

            jobs = dria_client.get_jobs()
            if jobs:
                logging.info(f"Jobs retrieved: {jobs}")
                public_key, private_key = generate_keys()
                push_content_topic({"type": "job", "public_key": public_key, "job": jobs[0]}, "synthesis")
            else:
                logging.warning("No available jobs")
        else:
            logging.warning("No available jobs")

    except Exception as e:
        logging.error(f"An error occurred while processing jobs: {e}")


if __name__ == "__main__":
    main()
