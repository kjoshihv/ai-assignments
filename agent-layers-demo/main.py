import os
import asyncio
import logging  # Import logging
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from perception import extract_facts
from memory import Memory
from decision import decide_next_step
from action import execute_action

# Configure logging
logging.basicConfig(
    filename="application.log",  # Log file
    level=logging.INFO,  # Log level
    format="%(filename)s %(funcName)s %(asctime)s - %(levelname)s - %(message)s"
)

os.environ["PYTHONIOENCODING"] = "utf-8"

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_FLASH_KEY")
client = genai.Client(api_key=api_key)

async def main():
    logging.info("Starting Chain of Thought Calculator")
    memory = Memory()

    try:
        server_params = StdioServerParameters(command="python", args=["agent-layers-demo\\cot_tools.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools_result = await session.list_tools()
                memory.update_tools_description(tools_result.tools)

                user_prompt = "Current monthly expense is 1,00,000 INR, inflation is 6%, calculate MONTHLY and YEARLY expense that required in year 2040? as a final answer."
                logging.info(f"User Input: {user_prompt}")                

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
- Provide only one STEP at a time.
- Provide calculation params in the format which can be executed by python eval function.
- Use **double quotes** around all keys and string values.
- Do not add any extra commentary or explanation.
- Return only valid JSON.

Example:
User: Current monthly expense is 2,00,000 INR, inflation is 5%, what will be the expense in a year 2050?
Assistant: {{"function_call": "show_reasoning", "params": ["[arithmetic] 1. First Calculate the number of years from now to future year 2050: (2050-2025) = 25", "[arithmetic] 2. Then calculate the future value using the formula: FV = PV * (1 + r) ** n. Where PV is the present value. r is the rate of inflation and n is the number of years. In oder to calculate this you can follow the below order: 1. Add 1 to the rate of inflation: (1 + 0.0565) = 1.0565 2. Raise the result to the power of the number of years: (1.0565) ** 25 = 3.95 3. Multiply the current monthly expense by the result: 2,00,000 * 3.95 = 7,90,000"]}}
User: Next step?
Assistant: {{"function_call": "calculate", "params": ["2050-2025"]}}
User: Result is 25. Let's verify this step.
Assistant: {{"function_call": "verify", "params": ["2050-2025", "25"]}}
User: Verified. Next step?
Assistant: {{"function_call": "calculate", "params": ["200000 * (1+0.0565) ** 25"]}}
User: Result is 7,90,000. Let's verify the final answer.
Assistant: {{"function_call": "verify", "params": ["200000 * (1+0.0565) ** 25","7,90,000"]}}
User: Verified correct.
Assistant: {{"final_answer": "7,90,000"}}
"""
                logging.info(f"System Prompt: {system_prompt}")
                # Extract key facts using the perception layer
                extracted_facts = await extract_facts(user_prompt, client)
                if not extracted_facts:
                    logging.error("Failed to extract key facts. Exiting...")
                
                # Store extracted facts in memory
                memory.store_extracted_facts(extracted_facts)
                logging.info(f"Extracted Key Facts: {extracted_facts}")
                current_step = None

                while True:
                    # Call decide_next_step with system_prompt and memory
                    decision = await decide_next_step(memory, client, system_prompt, current_step)
                    memory.update_decision_response(decision)

                    action_result = await execute_action(decision, session, memory)
                    if action_result.get("status", None) == "error":
                        logging.error(f"Error in action execution: {action_result['message']}")
                        break
                    current_step = action_result.get("message")
                    assistant_response = action_result.get("result")

                    if current_step == "final_answer":
                        logging.info(f"Final answer received {assistant_response}. Exiting...")
                        break
                    else:
                        current_step += f"\nUser: {current_step}"
                    if assistant_response:
                        memory.add_to_history(current_step, assistant_response)

                logging.info("Calculation completed!")

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
