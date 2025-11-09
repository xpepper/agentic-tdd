# Agentic TDD

Agentic TDD is a multi-agent Test-Driven Development (TDD) CLI tool that automates the development of code katas using specialized AI agents. The tool orchestrates four distinct agents to follow the classical TDD cycle: write a failing test, make it pass, and refactor – all while adhering to the requirements specified in a kata description file.

## Overview

The agentic-tdd tool uses multiple specialized AI agents to perform different roles in the TDD process:

- **Tester Agent**: Writes failing unit tests that capture the next required behavior
- **Implementer Agent**: Makes minimal changes to code to make tests pass
- **Refactorer Agent**: Improves code quality, readability, and maintainability
- **Supervisor Agent**: Oversees the process and intervenes when agents get stuck

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or Poetry

### Installation Options

#### Option 1: Using Virtual Environment (Recommended for Development)

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

2. Install in development mode:
```bash
pip install -e .[dev]
```

This installs the package in editable mode with development dependencies (pytest, ruff, mypy, etc.).

#### Option 2: Using Poetry

1. Install dependencies with Poetry:
```bash
poetry install
```

2. Activate the Poetry shell:
```bash
poetry shell
```

#### Option 3: Install from PyPI (Coming Soon)

Once published to PyPI, you'll be able to install directly:
```bash
pip install agentic-tdd
```

## Usage

Run agentic-tdd with a kata description file and LLM configuration:

```bash
agentic-tdd ~/path/to/kata_rules.md --model gpt-4 --provider openai --work-dir ./kata-output/
```

### Command Line Options

- `kata_description`: Path to the kata description file (required)
- `--model`: LLM model to use (default: gpt-4)
- `--provider`: LLM provider to use (default: openai)
- `--api-key`: API key for the LLM provider (can use env vars instead)
- `--base-url`: Base URL for the LLM provider (for OpenAI-compatible providers)
- `--work-dir`: Working directory for the TDD process (required)
- `--max-cycles`: Maximum number of TDD cycles to perform (default: 10)

### Environment Variables

Instead of passing the API key via command line, you can use environment variables:

```bash
export OPENAI_API_KEY="your-api-key"
# or for other providers:
export PERPLEXITY_API_KEY="your-api-key"
```

### Usage with Custom Base URLs

For OpenAI-compatible providers, you can specify a custom base URL:

```bash
agentic-tdd ~/path/to/kata_rules.md --model deepseek-coder --provider deepseek --base-url https://api.deepseek.com/ --work-dir ./kata-output/
```

This allows you to use providers like DeepSeek, iFlow, or any other OpenAI-compatible API by specifying the appropriate base URL.

## Example Kata Description

Create a markdown file with your kata requirements:

```markdown
# Simple Calculator Kata

Create a simple calculator that can perform basic arithmetic operations.

## Requirements

1. The calculator should be able to add two numbers
2. The calculator should be able to subtract two numbers
3. The calculator should be able to multiply two numbers
4. The calculator should be able to divide two numbers

## Constraints

- Division by zero should return an error or handle the case appropriately
- All operations should work with both positive and negative numbers
- The calculator should be implemented as a class or module with clear interfaces
```

## How It Works

The tool follows these steps:

1. Reads the kata description file to understand requirements
2. Initializes a git repository in the working directory
3. Begins the TDD cycle with the Tester Agent writing a failing test
4. The Implementer Agent makes the test pass with minimal changes
5. The Refactorer Agent improves code quality while keeping tests passing
6. The cycle repeats until the kata requirements are fulfilled or max cycles reached

Each step is committed to git with meaningful, conventional commit messages, creating a clear history of the development process. Files are named dynamically based on the kata content to make them more meaningful.

## Example Output

When running agentic-tdd, you'll see output like:

```
Agentic TDD starting with:
  Kata description: mars-rover-kata.md
  Model: sonar-pro
  Provider: perplexity
  Base URL: https://api.perplexity.ai
  Work directory: ./kata-output/
  Max cycles: 1
Supervisor: Starting TDD process...

--- Cycle 1 ---
Tester: Analyzing kata requirements and writing a new failing test...
Supervisor: Tester agent completed. New test fails as expected: True
Supervisor: Committed test changes: test: add failing test for cycle 1
Implementer: Implementing code to make tests pass...
Supervisor: Implementer agent completed. All tests pass: True
Supervisor: Committed implement changes: feat: implement code to pass test in cycle 1
Refactorer: Analyzing code for potential improvements...
Supervisor: Refactorer agent completed. All tests still pass: True
Supervisor: Committed refactor changes: refactor: improve code quality after cycle 1
Supervisor: Completed cycle 1

Agentic TDD completed: Supervisor agent completed 1 cycles
```

The resulting codebase in the work directory will contain implementation files and tests with meaningful names based on the kata content, along with a git history showing the TDD progression with conventional commit messages:
- `test: add failing test for cycle X` - When the Tester agent adds new tests
- `feat: implement code to pass test in cycle X` - When the Implementer agent implements functionality
- `refactor: improve code quality after cycle X` - When the Refactorer agent improves the code

## Architecture

The system is built with Python and uses LangChain to manage LLM interactions. It supports any LLM provider compatible with the OpenAI API standard.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting a pull request.

## License

MIT License

## Example Output

When running agentic-tdd, you'll see output like:

```
Agentic TDD starting with:
  Kata description: test_kata.md
  Model: gpt-4
  Provider: openai
  Work directory: ./test_output
  Max cycles: 2
Supervisor: Starting TDD process...

--- Cycle 1 ---
Tester: Analyzing kata requirements and writing a new failing test...
Supervisor: Tester agent completed. New test fails as expected: True
Implementer: Implementing code to make tests pass...
Supervisor: Implementer agent completed. All tests pass: True
Refactorer: Analyzing code for potential improvements...
Supervisor: Refactorer agent completed. All tests still pass: True
Supervisor: Committed changes: Cycle 1: TDD iteration completed
Supervisor: Completed cycle 1

Agentic TDD completed: Supervisor agent completed 1 cycles
```

The resulting codebase in the work directory will contain the implementation, tests, and a git history showing the TDD progression.
