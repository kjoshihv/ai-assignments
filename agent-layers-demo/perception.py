import re
from rich.console import Console
from pydantic import BaseModel, ValidationError
from utils import generate_with_timeout, remove_markdown

console = Console()

# Define a Pydantic model for the extracted fields
class ExtractedFacts(BaseModel):
    monthly_expense: int
    inflation_rate: float
    target_year: int
    goal: str

async def extract_facts(user_input, client):
    """Call the LLM to extract key facts from the user input."""
    console.print(f"[blue]Extracting facts from user input: {user_input} in {ExtractedFacts.__fields__.keys()} format.[/blue]")
    query = f"OUTPUT SHOULD BE STRICTLY VALID JSON FORMAT in the form of {ExtractedFacts.__fields__.keys()}. Extract key facts from this input: \n{user_input}"
    try:
        response = await generate_with_timeout(client, query)
        if response and response.text:
            cleaned_response = remove_markdown(response.text.strip()) 
            console.print(f"Extracted facts raw output {cleaned_response}, output type: {type(cleaned_response)}")
            try:
                # Validate the extracted fields using the Pydantic model
                extracted_facts = ExtractedFacts.model_validate_json(cleaned_response)
                console.print(f"Validated extracted facts: {extracted_facts.model_dump()}")
                return extracted_facts.model_dump()
            except ValidationError as e:
                console.print(f"[red]Validation Error: {e}[/red]")
                return None
        else:
            console.print("[red]Error: No response from LLM[/red]")
            return None
    except Exception as e:
        console.print(f"[red]Error extracting facts: {e}[/red]")
        return None
