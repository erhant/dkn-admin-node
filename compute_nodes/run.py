import json
import logging
import time

from pydantic import ValidationError

from compute_nodes.src.compute import run_ollama_with_prompt_and_context
from compute_nodes.src.constants import INPUT_CONTENT_TOPIC, OUTPUT_CONTENT_TOPIC
from compute_nodes.src.models.models import InputModel, OutputModel
from compute_nodes.src.waku.waku_rest import health_check, push_content_topic, subscribe_topic, get_content_topic

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def listen(content_topic):
    """Subscribe to a topic and process incoming messages continuously."""
    if health_check():
        logging.info("Waku is healthy. Proceeding to subscribe to content topic.")
        subscribe_topic(content_topic)
        logging.info(f"Subscribed to {content_topic}")
    else:
        logging.error("Waku is not healthy. Please check the system.")
        return

    while True:
        process_messages(content_topic)
        time.sleep(60)  # Polling interval, adjustable based on system requirements


def process_messages(content_topic):
    """Process messages from a subscribed topic."""
    try:
        message = get_content_topic(content_topic)
        if message:
            run(message)
    except Exception as e:
        logging.error(f"Error retrieving message from topic: {e}")


def run(message):
    """Decode, validate, process message and send response."""
    try:
        data = json.loads(message.payload.decode())
        validated_data = InputModel(**data)
        response = run_ollama_with_prompt_and_context(validated_data.prompt, validated_data.context)
        logging.info(f"Ollama response: {response}")

        output_model = OutputModel(result=response)
        push_content_topic(output_model, content_topic=OUTPUT_CONTENT_TOPIC)
    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
    except Exception as e:
        logging.error(f"Error processing message: {e}")


if __name__ == "__main__":
    listen(content_topic=INPUT_CONTENT_TOPIC)
