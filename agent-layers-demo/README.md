# Chain of Thought Calculator (CoT Calculator) using Agentic Cognitive Layers

The Chain of Thought Calculator is an intelligent agent application designed to solve complex mathematical reasoning problems step by step. It leverages four cognitive layers—Perception, Memory, Decision, and Action—to process user queries, reason through the problem, and provide accurate results.

## Overview

This application is built to simulate human-like reasoning by breaking down problems into smaller steps and solving them iteratively. It uses advanced AI models and tools to extract facts, make decisions, and execute actions while maintaining a structured memory of the process.

## Cognitive Layers

The application is structured around four key cognitive layers, each playing a critical role in the reasoning process:

### 1. Perception Layer
- **Role**: The perception layer is responsible for understanding and extracting key facts from the user's input.
- **Implementation**: It uses a language model to analyze the user's query and extract structured information such as numerical values, goals, and constraints.
- **Importance**: This layer ensures that the agent has a clear understanding of the problem before proceeding to solve it.
- **Key Functionality**:
  - Extracts facts using the `extract_facts` function.
  - Validates the extracted information using a Pydantic model (`ExtractedFacts`).

### 2. Memory Layer
- **Role**: The memory layer stores and manages the agent's knowledge throughout the reasoning process.
- **Implementation**: It maintains a record of the conversation history, extracted facts, tool descriptions, and responses from other layers.
- **Importance**: Memory allows the agent to keep track of its progress and ensures consistency in reasoning.
- **Key Functionality**:
  - Stores extracted facts, perception responses, and decision responses.
  - Updates tool descriptions and conversation history.

### 3. Decision Layer
- **Role**: The decision layer determines the next step in the reasoning process based on the current state of memory and the system prompt.
- **Implementation**: It uses a language model to decide whether to calculate, verify, or finalize the answer.
- **Importance**: This layer ensures that the agent follows a logical sequence of steps to solve the problem.
- **Key Functionality**:
  - Generates decisions using the `decide_next_step` function.
  - Validates decisions using a Pydantic model (`LLMResponse`).

### 4. Action Layer
- **Role**: The action layer executes the decisions made by the decision layer.
- **Implementation**: It interacts with *MCP tools* to perform calculations, verify results, or display reasoning.
- **Importance**: This layer bridges the gap between decision-making and execution, ensuring that the agent's reasoning is actionable.
- **Key Functionality**:
  - Executes actions such as `calculate`, `verify`, and `show_reasoning` using the `execute_action` function.
  - Handles errors and ensures the smooth execution of tasks.

## Features

- **Step-by-Step Reasoning**: The agent solves problems iteratively, showing its reasoning at each step.
- **Tool Integration**: The agent can call MCP tools for calculations and verifications.
- **Memory Management**: The agent maintains a structured memory of the reasoning process.
- **Email Notifications**: Users can set their preference to receive the final answer via Gmail.
- **Error Handling**: The agent gracefully handles errors and provides meaningful feedback.

## How It Works

1. **User Input**: The user provides a query, such as a mathematical problem, calculate future expenses.
2. **Perception**: The agent extracts key facts from the query.
3. **Memory Update**: The extracted facts are stored in memory.
4. **Decision**: The agent decides the next step based on the system prompt and memory.
5. **Action**: The agent executes the decision, such as performing a calculation or verifying a result.
6. **Iteration**: Steps 3, 4 and 5 are repeated until the final answer is reached.
7. **Final Answer**: The agent provides the final answer, either on the console or via Gmail.

## Example Query

**User Input**:  
_Current monthly expense is 2,00,000 INR, inflation is 5%, what will be the expense in the year 2050?_

**Agent Response**:  
1. Extracts facts: Monthly expense = 2,00,000 INR, Inflation rate = 5%, Target year = 2050.  
2. Shows reasoning: Calculates the number of years and applies the future value formula.  
3. Calculates and verifies each step.  
4. Provides the final answer: Monthly expense = 7,90,000 INR, Yearly expense = 94,80,000 INR.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/agent-layers-demo.git
   ```
2. Navigate to the project directory:
   ```bash
   cd agent-layers-demo
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

Follow the prompts to enter your query and optionally receive the final answer via email.

## Logging

All activities are logged in the `cot-application.log` file for debugging and tracking purposes.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
