
import ollama

from compute_nodes.src.constants import MODEL_NAME


def run_ollama_with_prompt_and_context(prompt, context):
    """
    This function runs the Ollama model with a given prompt and context.

    Parameters:
    - prompt (str): The prompt to provide to the Ollama model.
    - context (dict): The context to provide to the Ollama model.

    Returns:
    - response (dict): The response from the Ollama model.
    """
    # Run the Ollama model with the given prompt and context, and store the response
    response = ollama.chat(model=MODEL_NAME, messages=[
        {
            'role': 'user',
            'content': f'{context}\n\n{prompt}',
        },
    ])
    # Return the response from the Ollama model
    return response
