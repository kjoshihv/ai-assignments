from cognitive_layers.perception import PerceptionResult
from cognitive_layers.memory import MemoryItem
from typing import List, Optional
from dotenv import load_dotenv
from google import genai
import os
import logging

logging.basicConfig(
    filename="embeddings-demo.log",  # Log file
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_FLASH_KEY"))

def generate_plan(
    perception: PerceptionResult,
    memory_items: List[MemoryItem],
    tool_descriptions: Optional[str] = None
) -> str:
    """Generates a plan (tool call or final answer) using LLM based on structured perception and memory."""

    memory_texts = "\n".join(f"- {m.text}" for m in memory_items) or "None"

    tool_context = f"\nYou have access to the following tools:\n{tool_descriptions}" if tool_descriptions else ""

    prompt = f"""
You are a reasoning-driven AI agent with access to tools. Your job is to solve the user's request step-by-step by reasoning through the problem, selecting a tool if needed, and continuing until the FINAL_ANSWER is produced.{tool_context}

Always follow this loop:

1. Think step-by-step about the problem.
2. If a tool is needed, respond using the format:
   FUNCTION_CALL: tool_name|param1=value1|param2=value2
3. As a FINAL_ANSWER you have to call the appropriate tool open URLs in browser.
   FINAL_ANSWER: tool_name|param1=value1|param2=value2

Guidelines:
- Respond using EXACTLY ONE of the formats above per step.
- Do NOT include extra text, explanation, or formatting.
- Use nested keys (e.g., input.string) and square brackets for lists.
- You can reference these relevant memories:
{memory_texts}

Input Summary:
- User input: "{perception.user_input}"
- Intent: {perception.intent}
- Entities: {', '.join(perception.entities)}
- Tool hint: {perception.tool_hint or 'None'}

Examples:
- User asks: "Search a phrase 'what is google'". You have to follow below steps:
  1. FUNCTION_CALL: search_documents|query="what is google"  
    1.1 search_documents output: list of URLs from document having 'what is google' phrase
  2. FINAL_ANSWER: open_website|urls=[URLs]


IMPORTANT:
- Do NOT invent tools. Use only the tools listed below.
- If the question may relate to factual knowledge, use the 'search_documents' tool to look for the answer.
- If the previous tool output already contains factual information, DO NOT search again. Instead, summarize the relevant facts and respond with: FINAL_ANSWER: [your answer]
- Only repeat `search_documents` if the last result was irrelevant or empty.
- Do NOT repeat function calls with the same parameters.
- Do NOT output unstructured responses.
- Think before each step. Verify intermediate results mentally before proceeding.
- If unsure or no tool fits, skip to FINAL_ANSWER: [unknown]
- You have only 3 attempts. Final attempt must be FINAL_ANSWER]
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        raw = response.text.strip()
        logging.info(f"plan, LLM output: {raw}")

        for line in raw.splitlines():
            if line.strip().startswith("FUNCTION_CALL:") or line.strip().startswith("FINAL_ANSWER:"):
                return line.strip()

        return raw.strip()

    except Exception as e:
        logging.info(f"plan, Decision generation failed: {e}")
        return "FINAL_ANSWER: [unknown]"
