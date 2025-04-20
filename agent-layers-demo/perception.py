import logging  # Import logging
from pydantic import BaseModel, ValidationError
from utils import generate_with_timeout, remove_markdown

# Configure logging
logging.basicConfig(
    filename="cot-application.log",  # Log file
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ExtractedFacts(BaseModel):
    """
    Pydantic model for validating extracted facts.

    Attributes:
        monthly_expense (int): The monthly expense provided by the user.
        inflation_rate (float): The inflation rate provided by the user.
        target_year (int): The target year for the calculation.
        goal (str): The user's goal or query.
    """
    monthly_expense: int
    inflation_rate: float
    target_year: int
    goal: str

async def extract_facts(user_input, client):
    """
    Extract key facts from user input using the LLM.

    Args:
        user_input (str): The user's input query.
        client: The LLM client instance.

    Returns:
        dict: Validated extracted facts or None if extraction fails.
    """
    logging.info(f"Extracting facts from user input: {user_input}")
    query = f"OUTPUT SHOULD BE STRICTLY VALID JSON FORMAT in the form of {ExtractedFacts.__fields__.keys()}. Extract key facts from this input: \n{user_input}"
    try:
        # Call the LLM with the query
        response = await generate_with_timeout(client, query)
        if response and response.text:
            cleaned_response = remove_markdown(response.text.strip()) 
            try:
                # Validate the extracted fields using the Pydantic model
                extracted_facts = ExtractedFacts.model_validate_json(cleaned_response)
                logging.debug(f"Validated extracted facts: {extracted_facts.model_dump()}")
                return extracted_facts.model_dump()
            except ValidationError as e:
                logging.error(f"Validation Error: {e}")
                return None
        else:
            logging.error("No response from LLM")
            return None
    except Exception as e:
        logging.error(f"Error extracting facts: {e}", exc_info=True)
        return None
