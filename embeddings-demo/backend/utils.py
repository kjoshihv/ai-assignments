import re

def remove_markdown(response):
    """
    Remove code block markers from the response.

    Args:
        response (str): The response string.

    Returns:
        str: Cleaned response without markdown.
    """
    cleaned_response = re.sub(r'```(?:json|python|.*)?\n', '', response)
    cleaned_response = re.sub(r'\n```', '', cleaned_response)
    return cleaned_response