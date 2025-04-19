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

                next_step = "Current monthly expense is 1,00,000 INR, inflation is 6%, calculate MONTHLY and YEARLY expense that required in year 2040? as a final answer."
                logging.info(f"User Input: {next_step}")                

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
- Use **double quotes** around all keys and string values.
- Do not add any extra commentary or explanation.
- Return only valid JSON.
"""
                logging.info(f"System Prompt: {system_prompt}")
                # Extract key facts using the perception layer
                extracted_facts = await extract_facts(next_step, client)
                if not extracted_facts:
                    logging.error("Failed to extract key facts. Exiting...")
                
                # Store extracted facts in memory
                memory.store_extracted_facts(extracted_facts)
                logging.info(f"Extracted Key Facts: {extracted_facts}")

                while True:
                    # Call decide_next_step with system_prompt and memory
                    decision = await decide_next_step(memory, client, system_prompt)
                    action = decision.get("action", None)
                    params = decision.get("params")

                    if not action:
                        break

                    next_step, assistant_response = await execute_action(action, params, session, memory)
                    if next_step == "final_answer":
                        break
                    else:
                        system_prompt += f"\nUser: {next_step}"
                    if assistant_response:
                        memory.add_to_history(next_step, assistant_response)

                logging.info("Calculation completed!")

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
