from compute_nodes.src.models.models import InputModel, OutputModel

from pydantic import ValidationError
import json
from compute_nodes.src.compute import run_ollama_with_prompt_and_context
from compute_nodes.src.waku.waku_rest import health_check, push_content_topic, subscribe_topic, get_content_topic
from compute_nodes.src.constants import INPUT_CONTENT_TOPIC, OUTPUT_CONTENT_TOPIC


def listen(content_topic):
    # First, run a health check
    if health_check():
        print("Waku is healthy. Proceeding to subscribe to content topic.")
        # Subscribe to the given content topic on Waku
        subscribe_topic(content_topic)
        print(f"Subscribed to {content_topic}")
    else:
        print("Waku is not healthy. Please check the system.")

    while True:
        # Get the content from the content topic
        d = get_content_topic(content_topic)
        if d:
            run(d)


def run(message):
    try:
        # Decode the message
        data = json.loads(message.payload.decode())
        # Validate the input structure with Pydantic
        validated_data = InputModel(**data)
        # Run Ollama with the given prompt and context
        response = run_ollama_with_prompt_and_context(validated_data.prompt, validated_data.context)
        print(f"Ollama response: {response}")
        # Push the response to the content topic
        output_model = OutputModel(result=response, h="", s="", e="")
        push_content_topic(output_model, content_topic=OUTPUT_CONTENT_TOPIC)
    except ValidationError as ve:
        print(f"Validation error: {ve}")
    except Exception as e:
        print(f"Error processing message: {e}")


if __name__ == "__main__":
    listen(content_topic=INPUT_CONTENT_TOPIC)
