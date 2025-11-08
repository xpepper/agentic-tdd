# agentic-tdd

A multi-agent Test-Driven Development (TDD) CLI tool that develops code katas using AI agents.

## Overview

This tool implements a multi-agent system that follows the TDD process:
1. **Tester Agent**: Writes failing unit tests
2. **Implementer Agent**: Makes tests pass with minimal implementation
3. **Refactorer Agent**: Improves code quality while keeping tests passing
4. **Supervisor Agent**: Oversees the process and handles failures

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Usage

Basic run:
```bash
agentic-tdd kata-description.md
```

Dry-run (setup only, no workflow execution):
```bash
agentic-tdd kata-description.md --dry-run
```

Verbose output:
```bash
agentic-tdd kata-description.md --verbose
```

Limit cycles:
```bash
agentic-tdd kata-description.md --max-cycles 3
```

Specify model/provider:
```bash
agentic-tdd kata-description.md --model gpt-4o-mini --provider openai --api-key $OPENAI_API_KEY
```

## Development

See [AGENTS.md](AGENTS.md) for development guidelines and [PROJECT.md](PROJECT.md) for project goals.
