# MCP Paint Automation Project

This project demonstrates the use of MCP tools to perform mathematical operations and automate drawing tasks in Microsoft Paint. The project includes functionalities to open Paint, draw rectangles, and add text inside them. It also integrates LLM (Large Language Model) capabilities to perform iterative mathematical calculations and add the final result of these calculations inside the rectangle drawn in Paint.

## Features

- **Mathematical Operations**:
  - Perform addition, subtraction, multiplication, division, and more.
  - Calculate factorials, powers, square roots, and trigonometric functions.
  - Convert strings to ASCII values and compute exponential sums.

- **Paint Automation**:
  - Open Microsoft Paint programmatically.
  - Draw rectangles on the Paint canvas.
  - Add calculated math results inside the drawn rectangles.

- **Iterative Execution**:
  - Perform tasks in multiple phases with iterative steps.
  - Combine mathematical results with drawing operations.

- **LLM Integration**:
  - Use LLM to guide iterative execution for both mathematical and drawing tasks.
  - Dynamically generate and execute tool calls based on LLM responses.

## Technical Stack

- **Python**:
  - `pywinauto` and `pywin32` for Windows GUI automation.
  - `Pillow` for image processing.
  - `mcp` for defining and managing tools and prompts.
  - `dotenv` for environment variable management.

## Project Structure

```
start-with-mcp/
├── example2.py            # MCP tools and Paint automation logic
├── talk2mcp-2.py          # Iterative execution combining math and drawing
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd start-with-mcp
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Microsoft Paint is installed on your system (default on Windows).

## Usage

### 1. Perform Paint Operations
Run the `do-paint-operation.py` script to open Paint, draw a rectangle, and add text:
```bash
python do-paint-operation.py
```

### 2. Iterative Execution
Run the `talk2mcp-2.py` script to perform mathematical and drawing tasks iteratively:
```bash
python talk2mcp-2.py
```

## Tools and Functions

### Mathematical Tools
- `add(a, b)`: Add two numbers.
- `subtract(a, b)`: Subtract two numbers.
- `multiply(a, b)`: Multiply two numbers.
- `divide(a, b)`: Divide two numbers.
- `factorial(a)`: Compute the factorial of a number.
- `log(a)`: Compute the logarithm of a number.
- `strings_to_chars_to_int(string)`: Convert a string to ASCII values.
- `int_list_to_exponential_sum(int_list)`: Compute the sum of exponentials of a list of integers.
- And more...

### Paint Automation Tools
- `open_paint()`: Open and maximize Microsoft Paint.
- `draw_rectangle(x1, y1, x2, y2)`: Draw a rectangle in Paint.
- `add_text_in_paint(text)`: Add text inside a rectangle in Paint.

## License

MIT License - Feel free to use and modify as needed.
