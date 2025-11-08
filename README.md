# Agentic TDD

Agentic TDD is a multi-agent Test-Driven Development (TDD) CLI tool that automates the development of code katas using specialized AI agents. The tool orchestrates four distinct agents to follow the classical TDD cycle: write a failing test, make it pass, and refactor – all while adhering to the requirements specified in a kata description file.

## Overview

The agentic-tdd tool uses multiple specialized AI agents to perform different roles in the TDD process:

- **Tester Agent**: Writes failing unit tests that capture the next required behavior 
- **Implementer Agent**: Makes minimal changes to code to make tests pass
- **Refactorer Agent**: Improves code quality, readability, and maintainability
- **Supervisor Agent**: Oversees the process and intervenes when agents get stuck

## Installation

To install agentic-tdd, you'll need Python 3.8+ and pip:

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
- `--work-dir`: Working directory for the TDD process (required)
- `--max-cycles`: Maximum number of TDD cycles to perform (default: 10)

### Environment Variables

Instead of passing the API key via command line, you can use environment variables:

```bash
export OPENAI_API_KEY="your-api-key"
# or for other providers:
export PERPLEXITY_API_KEY="your-api-key"
```

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

Each step is committed to git, creating a clear history of the development process.

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