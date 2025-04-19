import json
import logging  # Import logging
from rich.console import Console
from cot_tools import ShowReasoningInput, CalculateInput, VerifyInput

# Configure logging
logging.basicConfig(
    filename="application.log",
    level=logging.INFO,
    format="%(filename)s %(funcName)s %(asctime)s - %(levelname)s - %(message)s"
)

console = Console()

async def execute_action(action, params, session, memory):
    """Execute the decided action."""
    logging.info(f"Executing action: {action} with params: {params}")
    try:
        if action == "show_reasoning":
            input_data = ShowReasoningInput(steps=params)
            await session.call_tool("show_reasoning", arguments=input_data.dict())
            logging.info("Action 'show_reasoning' executed successfully.")
            return "show_reasoning done, Next step?", None
        elif action == "calculate":
            input_data = CalculateInput(expression=params)
            calc_result = await session.call_tool("calculate", arguments=input_data.dict())
            if calc_result.content:
                value = json.loads(calc_result.content[0].text)["result"]
                logging.info(f"Calculation result: {value}")
                return f"Result is {value}. Let's verify this step.", value
        elif action == "verify":
            expression, expected = params
            input_data = VerifyInput(expression=expression, expected=expected)
            verify_response = await session.call_tool("verify", arguments=input_data.dict())
            value = json.loads(verify_response.content[0].text)
            if value.get("is_correct", False):
                logging.info("Verification successful.")
                return "Verified. Next step?", None
            else:
                logging.warning("Verification failed.")
                return "Not verified. Please re-do the calculation.", None
        elif action == "final_answer":
            answer = json.loads(params)
            monthly = answer.get("monthly_expense_2040", answer.get("monthly_expense"))
            yearly = answer.get("yearly_expense_2040", answer.get("yearly_expense"))
            logging.info(f"Final answer: Monthly: {monthly}, Yearly: {yearly}")
            console.print(f"\n\n[green]Your future expense for 2040, monthly: {monthly}, yearly: {yearly}[/green]")
            return "final_answer", None
        else:
            logging.warning(f"Unknown action: {action}")
        return None, None
    except Exception as e:
        logging.error(f"Error executing action '{action}': {e}", exc_info=True)
        return None, None
