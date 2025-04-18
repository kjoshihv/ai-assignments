import json
from rich.console import Console
from cot_tools import ShowReasoningInput, CalculateInput, VerifyInput

console = Console()

async def execute_action(action, params, session, memory):
    """Execute the decided action."""
    if action == "show_reasoning":
        input_data = ShowReasoningInput(steps=params)
        await session.call_tool("show_reasoning", arguments=input_data.dict())
    elif action == "calculate":
        input_data = CalculateInput(expression=params)
        calc_result = await session.call_tool("calculate", arguments=input_data.dict())
        if calc_result.content:
            value = json.loads(calc_result.content[0].text)["result"]
            return f"Result is {value}. Let's verify this step.", value
    elif action == "verify":
        expression, expected = params
        input_data = VerifyInput(expression=expression, expected=expected)
        verify_response = await session.call_tool("verify", arguments=input_data.dict())
        value = json.loads(verify_response.content[0].text)
        if value.get("is_correct", False):
            return "Verified. Next step?", None
        else:
            return "Not verified. Please re-do the calculation.", None
    elif action == "final_answer":
        answer = json.loads(params)
        monthly = answer.get("monthly_expense_2040", answer.get("monthly_expense"))
        yearly = answer.get("yearly_expense_2040", answer.get("yearly_expense"))
        console.print(f"\n\n[green]Your future expense for 2040, monthly: {monthly}, yearly: {yearly}[/green]")
        return None, None
    return None, None
