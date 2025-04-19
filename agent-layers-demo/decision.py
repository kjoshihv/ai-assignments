import logging  # Import logging
from utils import generate_with_timeout, remove_markdown
from pydantic import BaseModel, ValidationError
from typing import List, Optional

# Configure logging
logging.basicConfig(
    filename="application.log",
    level=logging.INFO,
    format="%(filename)s %(funcName)s %(asctime)s - %(levelname)s - %(message)s"
)

# Define a Pydantic model for the LLM response
class LLMResponse(BaseModel):
    function_call: Optional[str] = None
    params: Optional[List[str]] = None
    final_answer: Optional[str] = None
  
class LLMResponseList(BaseModel):
    response_list: List[LLMResponse]

async def decide_next_step(memory, client, system_prompt, current_step):
    """Decide the next step by calling the LLM with system_prompt and extracted facts."""
    # Fetch extracted facts from memory
    user_facts = memory.extracted_facts
    if not user_facts:
        raise ValueError("No extracted facts found in memory.")
    
    query = f"{system_prompt}\nSolve this problem step by step: {user_facts}\n{memory.get_decision_response()} \n {current_step}"

    logging.info(f"Deciding next step with query: {query}")

    # Call the LLM
    response = await generate_with_timeout(client, query)
    if not response or not response.text:
        return {"action": None, "params": None}

    # Parse and validate the LLM response
    try:
        cleaned_response = remove_markdown(response.text.strip()) 
        logging.info(f"Decision raw output: {cleaned_response}")
        decision_output = LLMResponse.model_validate_json(cleaned_response)
    except ValidationError as e:
        logging.error(f"Decision layer. Validation Error: {e}")
        return {"action": None, "params": None}

    decision_out_json = decision_output.model_dump()
    return decision_out_json
