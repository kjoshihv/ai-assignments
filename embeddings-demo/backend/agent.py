import asyncio
import time
import os
import datetime
from cognitive_layers.perception import extract_perception
from cognitive_layers.memory import MemoryManager, MemoryItem
from cognitive_layers.decision import generate_plan
from cognitive_layers.action import execute_tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import logging

logging.basicConfig(
    filename="embeddings-demo.log",  # Log file
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s"
)

max_steps = 3

async def start_search(user_input: str):
    try:
        logging.info("Starting agent...")
        
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"],
            cwd="D:\\code\\agentic-ai\\ai-assignments\\embeddings-demo\\backend"
        )

        try:
            async with stdio_client(server_params) as (read, write):
                try:
                    async with ClientSession(read, write) as session:
                        logging.info("[agent] Session created, initializing...")
 
                        try:
                            await session.initialize()
                            logging.info("[agent] MCP session initialized")

                            tools = await session.list_tools()
                            # logging.info("Available tools:" [t.name for t in tools.tools])

                            # Get available tools
                            logging.info("Requesting tool list...")
                            tools_result = await session.list_tools()
                            tools = tools_result.tools
                            tool_descriptions = "\n".join(
                                f"- {tool.name}: {getattr(tool, 'description', 'No description')}" 
                                for tool in tools
                            )

                            logging.info(f"agent: {len(tools)} tools loaded. {tool_descriptions}")

                            memory = MemoryManager()
                            session_id = f"session-{int(time.time())}"
                            query = user_input
                            step = 0

                            while step < max_steps:
                                logging.info(f"loop, Step {step + 1} started")

                                perception = extract_perception(user_input)
                                logging.info(f"perception, Intent: {perception.intent}, Tool hint: {perception.tool_hint}")

                                retrieved = memory.retrieve(query=user_input, top_k=3, session_filter=session_id)
                                logging.info(f"memory, Retrieved {len(retrieved)} relevant memories")

                                plan = generate_plan(perception, retrieved, tool_descriptions=tool_descriptions)
                                logging.info(f"plan, Plan generated: {plan}")

                                try:
                                    result = await execute_tool(session, tools, plan)
                                    logging.info(f"tool, {result.tool_name} returned: {result.result}")

                                    memory.add(MemoryItem(
                                        text=f"Tool call: {result.tool_name} with {result.arguments}, got: {result.result}",
                                        type="tool_output",
                                        tool_name=result.tool_name,
                                        user_query=user_input,
                                        tags=[result.tool_name],
                                        session_id=session_id
                                    ))

                                    user_input = f"Original task: {query}\nPrevious output: {result.result}\nWhat should I do next?"
                                    # return result.result

                                    if plan.startswith("FINAL_ANSWER:"):
                                        logging.info(f"agent, FINAL RESULT: {plan}")
                                        return

                                except Exception as e:
                                    logging.info(f"error, Tool execution failed: {e}")
                                    break

                                step += 1
                        except Exception as e:
                            logging.error(f"[agent] Session initialization error: {str(e)}")
                except Exception as e:
                    logging.errro(f"[agent] Session creation error: {str(e)}")
        except Exception as e:
            logging.error(f"[agent] Connection error: {str(e)}")
    except Exception as e:
        logging.error(f"[agent] Overall error: {str(e)}")

    logging.info("Agent session complete.")
