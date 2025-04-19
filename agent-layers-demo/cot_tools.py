from mcp.server.fastmcp import FastMCP
from rich.table import Table
from rich import box
import re
import logging  # Add logging import

mcp = FastMCP("CoTCalculator")

# Configure logging
logging.basicConfig(
    filename="application.log",
    level=logging.INFO,
    format="%(filename)s %(funcName)s %(asctime)s - %(levelname)s - %(message)s"
)


@mcp.tool()
def show_reasoning(steps: list) -> dict:
    """Show the step-by-step reasoning process"""
    logging.info("[blue]FUNCTION CALL:[/blue] show_reasoning()")
    for i, step in enumerate(steps, 1):
        logging.info(f"Step {i}: {step}")
    return {"status": "success", "message": "Reasoning shown"}

@mcp.tool()
def calculate(expression: str) -> dict:
    """Calculate the result of an expression"""
    logging.info("FUNCTION CALL: calculate()")
    logging.info(f"Expression:{expression}")
    try:
        result = eval(expression)
        logging.info(f"Result: {result}")
        return {"result": result}
    except Exception as e:
        logging.info(f"Error: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
def verify(expression: str, expected_arg: str) -> dict:
    """Verify if a calculation is correct"""
    logging.info("[blue]FUNCTION CALL:[/blue] verify()")
    logging.info(f"[blue]Verifying:[/blue] {expression} = {expected_arg}")
    try:
        actual = float(eval(expression))
        expected = float(eval(expected_arg))
        is_correct = abs(actual - float(expected)) < 1e-10
        
        if is_correct:
            logging.info(f"[green]Correct! {expression} = {expected}[/green]")
        else:
            logging.info(f"[red]Incorrect! {expression} should be {actual}, got {expected}[/red]")
            
        return {"is_correct": is_correct, "actual": actual, "expected": expected}
    except Exception as e:
        logging.info(f"[red]Error:[/red] {str(e)}")
        return {"error": str(e)}

def check_consistency(steps: list) -> dict:
    """Check if calculation steps are consistent with each other"""
    logging.info("FUNCTION CALL: check_consistency()")
    
    try:
        # Create a table for step analysis
        table = Table(
            title="Step-by-Step Consistency Analysis",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Step", style="cyan")
        table.add_column("Expression", style="blue")
        table.add_column("Result", style="green")
        table.add_column("Checks", style="yellow")

        issues = []
        warnings = []
        insights = []
        previous = None
        
        for i, (expression, result) in enumerate(steps, 1):
            checks = []
            
            # 1. Basic Calculation Verification
            try:
                expected = eval(expression)
                if abs(float(expected) - float(result)) < 1e-10:
                    checks.append("[green]✓ Calculation verified[/green]")
                else:
                    issues.append(f"Step {i}: Calculation mismatch")
                    checks.append("[red]✗ Calculation error[/red]")
            except:
                warnings.append(f"Step {i}: Couldn't verify calculation")
                checks.append("[yellow]! Verification failed[/yellow]")

            # 2. Dependency Analysis
            if previous:
                prev_expr, prev_result = previous
                if str(prev_result) in expression:
                    checks.append("[green]✓ Uses previous result[/green]")
                    insights.append(f"Step {i} builds on step {i-1}")
                else:
                    checks.append("[blue]○ Independent step[/blue]")

            # 3. Magnitude Check
            if previous and result != 0 and previous[1] != 0:
                ratio = abs(result / previous[1])
                if ratio > 1000:
                    warnings.append(f"Step {i}: Large increase ({ratio:.2f}x)")
                    checks.append("[yellow]! Large magnitude increase[/yellow]")
                elif ratio < 0.001:
                    warnings.append(f"Step {i}: Large decrease ({1/ratio:.2f}x)")
                    checks.append("[yellow]! Large magnitude decrease[/yellow]")

            # 4. Pattern Analysis
            operators = re.findall(r'[\+\-\*\/\(\)]', expression)
            if '(' in operators and ')' not in operators:
                warnings.append(f"Step {i}: Mismatched parentheses")
                checks.append("[red]✗ Invalid parentheses[/red]")

            # 5. Result Range Check
            if abs(result) > 1e6:
                warnings.append(f"Step {i}: Very large result")
                checks.append("[yellow]! Large result[/yellow]")
            elif abs(result) < 1e-6 and result != 0:
                warnings.append(f"Step {i}: Very small result")
                checks.append("[yellow]! Small result[/yellow]")

            # Add row to table
            table.add_row(
                f"Step {i}",
                expression,
                f"{result}",
                "\n".join(checks)
            )
            
            previous = (expression, result)

        # Display Analysis
        logging.info("Consistency Analysis Report")
        # Replace console.print calls with logging for issues, warnings, and insights
        if issues:
            logging.error("Critical Issues:\n" + "\n".join(issues))

        if warnings:
            logging.warning("Warnings:\n" + "\n".join(warnings))

        if insights:
            logging.info("Insights:\n" + "\n".join(insights))

        # Final Consistency Score
        total_checks = len(steps) * 5  # 5 types of checks per step
        passed_checks = total_checks - (len(issues) * 2 + len(warnings))
        consistency_score = (passed_checks / total_checks) * 100

        logging.info(f"Consistency Score: {consistency_score:.1f}%")
        return {
            "consistency_score": consistency_score,
            "issues": issues,
            "warnings": warnings,
            "insights": insights
        }
    except Exception as e:
        logging.error(f"Error in consistency check: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()
    else:
        mcp.run(transport="stdio")
