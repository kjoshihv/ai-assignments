import logging  # Import logging
from utils import generate_with_timeout, remove_markdown
from pydantic import BaseModel, ValidationError
from typing import List, Optional

# Configure logging
logging.basicConfig(
    filename="cot-application.log",  # Log file
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class FinalAnswer(BaseModel):
    """
    Model for the final answer containing monthly and yearly expenses.

    Attributes:
        monthly (float): The calculated monthly expense.
        yearly (float): The calculated yearly expense.
    """
    monthly: float
    yearly: float

# Define a Pydantic model for the LLM response
class LLMResponse(BaseModel):
    """
    Model for the response from the LLM.

    Attributes:
        function_call (Optional[str]): The function to call.
        params (Optional[List[str]]): Parameters for the function call.
        final_answer (Optional[FinalAnswer]): The final answer, if available.
    """
    function_call: Optional[str] = None
    params: Optional[List[str]] = None
    final_answer: Optional[FinalAnswer] = None  # Updated to dict with monthly and yearly expense

class LLMResponseList(BaseModel):
    response_list: List[LLMResponse]

async def decide_next_step(memory, client, system_prompt, current_step):
    """
    Decide the next step by calling the LLM with system_prompt and extracted facts.

    Args:
        memory: The memory object containing conversation history and facts.
        client: The LLM client instance.
        system_prompt (str): The system prompt for the LLM.
        current_step (str): The current step in the reasoning process.

    Returns:
        dict: The decision output from the LLM.
    """
    # Fetch extracted facts from memory
    user_facts = memory.extracted_facts
    if not user_facts:
        raise ValueError("No extracted facts found in memory.")
    
    if memory.get_decision_response() and current_step:
      query = f"{system_prompt}\nSolve this problem step by step: {user_facts}\n{memory.get_decision_response()}\n{current_step}"
    elif memory.get_decision_response():
      query = f"{system_prompt}\nSolve this problem step by step: {user_facts}\n{memory.get_decision_response()}"
    else:
      query = f"{system_prompt}\nSolve this problem step by step: {user_facts}"

    logging.info(f"Deciding next step with prompt:\n {query}\n")

    # Call the LLM
    response = await generate_with_timeout(client, query)
    if not response or not response.text:
        return {"status": "Error", "error_message": None}

    # Parse and validate the LLM response
    try:
        cleaned_response = remove_markdown(response.text.strip()) 
        logging.info(f"\nDecision:\n{cleaned_response}")
        decision_output = LLMResponse.model_validate_json(cleaned_response)
    except ValidationError as e:
        logging.error(f"Decision layer. Validation Error: {e}")
        return {"status": "Error", "error_message": f"Exception: {e}"}

    decision_out_json = decision_output.model_dump()
    return decision_out_json
