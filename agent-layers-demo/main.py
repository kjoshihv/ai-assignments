import os
import asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from rich.console import Console
from rich.panel import Panel
from perception import extract_facts
from memory import Memory
from decision import decide_next_step
from action import execute_action
from utils import generate_with_timeout  # Import from utils

os.environ["PYTHONIOENCODING"] = "utf-8"

console = Console()

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_FLASH_KEY")
client = genai.Client(api_key=api_key)

async def main():
    console.print(Panel("Chain of Thought Calculator, calculates future personal expense", border_style="cyan"))
    memory = Memory()

    try:
        server_params = StdioServerParameters(command="python", args=["agent-layers-demo\\cot_tools.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools_result = await session.list_tools()
                memory.update_tools_description(tools_result.tools)

                user_input = "Current monthly expense is 2,00,000 INR, inflation is 5%, calculate MONTHLY and YEARLY expense that required in year 2040? as a final answer."
                console.print(Panel(f"User Input: {user_input}", border_style="cyan"))

                # Extract key facts using the perception layer
                extracted_facts = await extract_facts(user_input, client)
                if not extracted_facts:
                    console.print("[red]Failed to extract key facts. Exiting...[/red]")
                    return

                # Store extracted facts in memory
                memory.store_extracted_facts(extracted_facts)

                console.print(Panel(f"Extracted Key Facts:\n\n[blue]{extracted_facts}[/blue]"))

                system_prompt = f"""You are a mathematical reasoning agent that solves problems step by step.
You have access to these tools:
{memory.tools_description}

First show your REASONING, then CALCULATE and VERIFY each step.

Respond with EXACTLY ONE line, containing only a strictly valid JSON object in one of these formats:
    1. For function calls:
        {{"function_call": "function_name", "params": ["param1", "param2", ...]}}

    2. For final answers:
        {{"final_answer": "answer"}}

    3. For error messages or failure:
        {{"error": "Error message"}}

IMPORTANT:
- Use **double quotes** around all keys and string values.
- Do not add any extra commentary or explanation.
- Return only valid JSON.
"""
                console.print(Panel(f"System Prompt:\n\n[blue]{system_prompt}[/blue]"))

                while True:
                    # Call decide_next_step with system_prompt and memory
                    decision = await decide_next_step(memory, client, system_prompt)
                    action = decision.get("action", None)
                    params = decision.get("params")

                    if not action:
                        break

                    user_input, assistant_response = await execute_action(action, params, session, memory)
                    if user_input:
                        system_prompt += f"\nUser: {user_input}"
                    if assistant_response:
                        memory.add_to_history(user_input, assistant_response)

                console.print("\n[green]Calculation completed![/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
