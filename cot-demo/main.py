import os
import re
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
from concurrent.futures import TimeoutError
from rich.console import Console
from rich.panel import Panel
import json

console = Console()

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_FLASH_KEY")
client = genai.Client(api_key=api_key)



def remove_markdown(response):
    # Remove code block markers
    cleaned_response = re.sub(r'```(?:json|python|.*)?\n', '', response)
    cleaned_response = re.sub(r'\n```', '', cleaned_response)
    return cleaned_response



async def generate_with_timeout(client, prompt, timeout=20):
    """Generate content with a timeout"""
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        return response
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return None

async def get_llm_response(client, prompt):
    """Get response from LLM with timeout"""
    response = await generate_with_timeout(client, prompt)
    if response and response.text:
        return response.text.strip()
    return None

async def main():
    console.print(Panel("Chain of Thought Calculator", border_style="cyan"))
    try:
        server_params = StdioServerParameters(
            command="python", args=["cot-demo\cot_tools.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Get available tools
                print("Requesting tool list...")
                tools_result = await session.list_tools()
                tools = tools_result.tools

                try:
                    tools_description = []
                    for i, tool in enumerate(tools):
                        try:
                            # Get tool properties
                            params = tool.inputSchema
                            desc = getattr(
                                tool, "description", "No description available"
                            )
                            name = getattr(tool, "name", f"tool_{i}")

                            # Format the input schema in a more readable way
                            if "properties" in params:
                                param_details = []
                                for param_name, param_info in params[
                                    "properties"
                                ].items():
                                    param_type = param_info.get("type", "unknown")
                                    param_details.append(f"{param_name}: {param_type}")
                                params_str = ", ".join(param_details)
                            else:
                                params_str = "no parameters"

                            tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                            tools_description.append(tool_desc)
                        except Exception as e:
                            print(f"Error processing tool {i}: {e}")
                            tools_description.append(f"{i+1}. Error processing tool")

                    tools_description = "\n".join(tools_description)
                except Exception as e:
                    print(f"Error creating tools description: {e}")
                    tools_description = "Error loading tools"

                print("Creating system prompt...")

                system_prompt_1 = f"""You are a mathematical reasoning agent that solves problems step by step.
You have access to these tools:
{tools_description}

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

Example:
User: Current monthly expense is 2,00,000 INR, inflation is 5%, what will be the expense in a year 2050?
Assistant: {{"function_call": "show_reasoning", "params": ["[arithmetic] 1. First Calculate the number of years from now to future year 2050: (2050-2025) = 25", "[arithmetic] 2. Then calculate the future value using the formula: FV = PV * (1 + r)^n. Where PV is the present value. r is the rate of inflation and n is the number of years. In oder to calculate this you can follow the below order: 1. Add 1 to the rate of inflation: (1 + 0.0565) = 1.0565 2. Raise the result to the power of the number of years: (1.0565) ^ 25 = 3.95 3. Multiply the current monthly expense by the result: 2,00,000 * 3.95 = 7,90,000"]}}
User: Next step?
Assistant: {{"function_call": "calculate", "param": "2050-2025"}}
User: Result is 25. Let's verify this step.
Assistant: {{"function_call": "verify", "params": ["2050-2025", 25]}}
User: Verified. Next step?
Assistant: {{"function_call": "calculate", "param": "200000 * (1+0.0565) ^25"}}
User: Result is 7,90,000. Let's verify the final answer.
Assistant: {{"function_call": "verify", "params": ["200000 * (1+0.0565) ^25", 790000]}}
User: Verified correct.
Assistant: {{"final_answer": "7,90,000"}}

"""

                console.print(Panel("System Prompt Start", border_style="blue"))
                console.print(Panel(system_prompt_1))
                print("="*10, "System Prompt End", "="*10)

                problem = "Current monthly expense is 2,00,000 INR, inflation is 5%, calculate the expense that required in year 2040?"
                console.print(Panel(f"Problem: {problem}", border_style="cyan"))

                # Initialize conversation
                prompt = f"{system_prompt_1}\n\nSolve this problem step by step: {problem}"
                conversation_history = []

                while True:
                    console.print("Generating LLM response")
                    response = await generate_with_timeout(client, prompt)
                    if not response or not response.text:
                        break

                    result_str = response.text.strip()
                    console.print(f"\n[yellow]ASSISTANT:[/yellow] {result_str}")

                    try:
                        removed_markdown=remove_markdown(result_str)
                        result = json.loads(removed_markdown)
                    except json.JSONDecodeError as e:
                        console.print(f"[red]Error parsing JSON: {e}[/red]")
                        break

                    if result.get("function_call", None):
                        func_name = result["function_call"]

                        if func_name == "show_reasoning":
                            console.print("Showing reasoning steps")
                            # Call the show_reasoning tool
                            params = result.get("params", [])
                            await session.call_tool(
                                "show_reasoning", arguments={"steps": params}
                            )
                            prompt += "\nUser: Next step?"

                        elif func_name == "calculate":
                            console.print("Calculating expression")
                            expression = result.get("param",None)
                            calc_result = await session.call_tool(
                                "calculate", arguments={"expression": expression}
                            )
                            if calc_result.content:
                                value = calc_result.content[0].text
                                prompt += f"\nUser: Result is {value}. Let's verify this step."
                                conversation_history.append((expression, value))

                        elif func_name == "verify":
                            params = result.get("params", [])
                            console.print("Verifying calculation step", params[0], params[1])
                            expression, expected = params[0], params[1]
                            await session.call_tool(
                                "verify",
                                arguments={
                                    "expression": expression,
                                    "expected": expected,
                                },
                            )
                            prompt += "\nUser: Verified. Next step?"                        
                        else:
                            print(f"Unknown function call: {func_name}")
                            break
                    elif result.get("final_answer", None):
                            # Verify the final answer against the original problem
                            if conversation_history:
                                final_answer = float(
                                    result["final_answer"][0]
                                )
                                await session.call_tool(
                                    "verify",
                                    arguments={
                                        "expression": problem,
                                        "expected": final_answer,
                                    },
                                )
                            break
                    prompt += f"\nAssistant: {result}"
                console.print("\n[green]Calculation completed![/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
