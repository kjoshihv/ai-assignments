import logging  # Import logging
from utils import generate_with_timeout, remove_markdown
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Union

# Configure logging
logging.basicConfig(
    filename="application.log",
    level=logging.INFO,
    format="%(filename)s %(funcName)s %(asctime)s - %(levelname)s - %(message)s"
)

# Define a Pydantic model for the LLM response
class LLMResponse(BaseModel):
    function_call: Optional[str] = None
    params: Optional[Union[List[str], str]] = None
    final_answer: Optional[str] = None
  
class LLMResponseList(BaseModel):
    response_list: List[LLMResponse]

async def decide_next_step(memory, client, system_prompt):
    """Decide the next step by calling the LLM with system_prompt and extracted facts."""
    # Fetch extracted facts from memory
    decision_output = memory.extracted_facts
    if not decision_output:
        raise ValueError("No extracted facts found in memory.")
    
    # system_prompt = system_prompt + f"\nRespond with EXACTLY ONE line in the form of given keys: {LLMResponse.__fields__.keys()}"

    # Prepare the query for the LLM
    query = f"{system_prompt}\nHere is the problem in JSON format: {decision_output}, you have to solve it STEP BY STEP only and make sure to Respond with EXACTLY ONE STEP"

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
    # Process the validated response
    if decision_out_json.get("function_call", None):
        return {"action": decision_out_json.get("function_call"), "params": decision_out_json.get("params")}
    elif decision_out_json.get("final_answer", None):
        return {"action": "final_answer", "params": decision_out_json.get("final_answer")}
    return {"action": None, "params": None}
