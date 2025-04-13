# Chain of Thought (CoT) Calculator

The `cot-demo` project demonstrates the use of a Chain of Thought (CoT) reasoning approach to solve mathematical problems step-by-step. It integrates with tools to perform calculations, verify results in reasoning.

Validate Prompts with ChatGPT with certain criterias. See `Criteria for Prompt validation` section.

## Features

- **Step-by-Step Reasoning**:
  - Breaks down problems into smaller steps.
  - Provides reasoning for each step before performing calculations.

- **Tool Integration**:
  - Supports tools for calculations, verification, and reasoning analysis.
  - Includes tools like `calculate`, `verify`, and `show_reasoning`.

- **Interactive Execution**:
  - Displays results and reasoning in a structured format.

## Technical Stack

- **Python**:
  - `mcp` for tool integration and reasoning management.
  - `rich` for enhanced console output.
  - `dotenv` for environment variable management.

## Criteria for Prompt validation

1. ✅ Explicit Reasoning Instructions  
   - Does the prompt tell the model to reason step-by-step?  
   - Does it include instructions like “explain your thinking” or “think before you answer”?

2. ✅ Structured Output Format  
   - Does the prompt enforce a predictable output format (e.g., FUNCTION_CALL, JSON, numbered steps)?  
   - Is the output easy to parse or validate?

3. ✅ Separation of Reasoning and Tools  
   - Are reasoning steps clearly separated from computation or tool-use steps?  
   - Is it clear when to calculate, when to verify, when to reason?

4. ✅ Conversation Loop Support  
   - Could this prompt work in a back-and-forth (multi-turn) setting?  
   - Is there a way to update the context with results from previous steps?

5. ✅ Instructional Framing  
   - Are there examples of desired behavior or “formats” to follow?  
   - Does the prompt define exactly how responses should look?

6. ✅ Internal Self-Checks  
   - Does the prompt instruct the model to self-verify or sanity-check intermediate steps?

7. ✅ Reasoning Type Awareness  
   - Does the prompt encourage the model to tag or identify the type of reasoning used (e.g., arithmetic, logic, lookup)?

8. ✅ Error Handling or Fallbacks  
   - Does the prompt specify what to do if an answer is uncertain, a tool fails, or the model is unsure?

9. ✅ Overall Clarity and Robustness  
   - Is the prompt easy to follow?  
   - Is it likely to reduce hallucination and drift?

## Project Structure

```
cot-demo/
├── main.py            # Main script for CoT reasoning and tool integration
├── cot_tools.py       # Tools for calculation, verification, and reasoning
├── README.md          # Project documentation
├── pyproject.toml     # Project metadata and dependencies
└── .python-version    # Python version specification
```

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd cot-demo
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API key:
   ```
   GEMINI_FLASH_KEY=your_api_key_here
   ```

4. Ensure Python 3.11 is installed (as specified in `.python-version`).

## Usage

1. Run the main script:
   ```bash
   python main.py
   ```

2. Follow the prompts to solve mathematical problems step-by-step.

3. View reasoning, calculations, and consistency analysis in the console.

## Tools

- **show_reasoning(steps: list)**:
  - Displays the reasoning steps in a structured format.

- **calculate(expression: str)**:
  - Evaluates a mathematical expression and returns the result.

- **verify(expression: str, expected: float)**:
  - Verifies if a calculation result matches the expected value.

## Example Problem

### Input:
```
Current monthly expense is 2,00,000 INR, inflation is 5%. Calculate MONTHLY and YEARLY expense required in the year 2040.
```

### Output:
- Step-by-step reasoning and calculations.
- Final answer with monthly and yearly expenses for 2040.

## License

MIT License - Feel free to use and modify as needed.
