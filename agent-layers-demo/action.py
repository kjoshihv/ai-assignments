import json
import logging  # Import logging

# Configure logging
logging.basicConfig(
    filename="cot-application.log",  # Log file
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def execute_action(decision, session, memory):
    """Execute the decided action based on the decision object."""
    action = "final_answer" if decision.get("final_answer", None) else decision.get("function_call", None)
    params = decision.get("params")
    logging.info(f"Action: `{action}`, params: {params}")
    try:
        if action == "show_reasoning":
            await session.call_tool("show_reasoning", arguments={"steps": params})
            logging.info("Action 'show_reasoning' executed successfully.")
            return {"status": "success", "message": "User: show_reasoning done, Next step?", "result": None}
        elif action == "calculate":
            logging.info(f"Calculating with expression: {params}")
            calc_result = await session.call_tool("calculate", arguments={"expression": params[0]})
            if calc_result.content:
                value = json.loads(calc_result.content[0].text)
                logging.info(f"Calculation result: {value}")
                return {"status": "success", "message": f"User: Result is {value}. Let's verify this step.", "result": value}
        elif action == "verify":
            verify_response = await session.call_tool("verify", arguments={
                                    "expression": params[0],
                                    "expected_arg": params[1],
                                })
            value = json.loads(verify_response.content[0].text)
            if value.get("is_correct", False):
                logging.info("Verification successful.")
                return {"status": "success", "message": "User: Verified. Next step?", "result": None}
            else:
                logging.warning("Verification failed.")
                return {"status": "failure", "message": "User: Not verified. Please re-do the calculation.", "result": None}
        elif action == "final_answer":
            return {"status": "success", "message": "final_answer", "result": decision.get("final_answer")}
        else:
            logging.warning(f"Unknown action: {action}")
            return {"status": "failure", "message": "Unknown action", "result": None}
    except Exception as e:
        logging.error(f"Error executing action '{action}': {e}", exc_info=True)
        return {"status": "error", "message": f"Error: {str(e)}", "result": None}
