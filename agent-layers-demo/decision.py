from utils import generate_with_timeout, remove_markdown  # Import the LLM utility
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Union
from rich.console import Console

console = Console()

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
    
    system_prompt = system_prompt + f"\nOUTPUT SHOULD BE STRICTLY VALID JSON FORMAT in the python list form of [{LLMResponseList.__fields__.keys()}]"

    # Prepare the query for the LLM
    query = f"{system_prompt}\n\nSolve this problem step by step: {decision_output}"

    console.print(f"[yellow]Deciding next step with query: {query}[/yellow]")

    # Call the LLM
    response = await generate_with_timeout(client, query)
    if not response or not response.text:
        return {"action": None, "params": None}

    # Parse and validate the LLM response
    try:
        cleaned_response = remove_markdown(response.text.strip()) 
        console.print(f"Decision raw output {cleaned_response}, output type: {type(cleaned_response)}")
        valid_list = LLMResponseList.model_validate_json(cleaned_response)
        console.print(f"Type of list {type(valid_list)}, value: {valid_list.response_list}")
        for item in valid_list.response_list:
            console.print("Validating item as string")
            decision_output = LLMResponse.model_validate_json(item.model_dump_json())
        console.print(f"Validated extracted facts: {decision_output.model_dump()}")
    except ValidationError as e:
        console.print(f"[red]Validation Error: {e}[/red]")
        return {"action": None, "params": None}
    console.print("[green]Wooooo Validation for decision done[/green]")

    decision_out_json = decision_output.model_dump()
    # Process the validated response
    if decision_out_json.get("function_call", None):
        return {"action": decision_out_json.get("function_call"), "params": decision_out_json.get("params")}
    elif decision_out_json.get("final_answer", None):
        return {"action": "final_answer", "params": decision_out_json.get("final_answer")}
    return {"action": None, "params": None}
