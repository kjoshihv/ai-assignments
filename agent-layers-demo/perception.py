import logging  # Import logging
from pydantic import BaseModel, ValidationError
from utils import generate_with_timeout, remove_markdown

# Configure logging
logging.basicConfig(
    filename="application.log",
    level=logging.INFO,
    format="%(filename)s %(funcName)s %(asctime)s - %(levelname)s - %(message)s"
)

# Define a Pydantic model for the extracted fields
class ExtractedFacts(BaseModel):
    monthly_expense: int
    inflation_rate: float
    target_year: int
    goal: str
    # next_step_for_user: Optional[str] = None

async def extract_facts(user_input, client):
    """Call the LLM to extract key facts from the user input."""
    logging.info(f"Extracting facts from user input: {user_input}")
    query = f"OUTPUT SHOULD BE STRICTLY VALID JSON FORMAT in the form of {ExtractedFacts.__fields__.keys()}. Extract key facts from this input: \n{user_input}"
    try:
        response = await generate_with_timeout(client, query)
        if response and response.text:
            cleaned_response = remove_markdown(response.text.strip()) 
            logging.info(f"Extracted facts raw output: {cleaned_response}")
            try:
                # Validate the extracted fields using the Pydantic model
                extracted_facts = ExtractedFacts.model_validate_json(cleaned_response)
                logging.info(f"Validated extracted facts: {extracted_facts.model_dump()}")
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
