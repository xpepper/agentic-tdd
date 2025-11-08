"""CLI entry point for the agentic-tdd tool."""

import argparse
import sys
import os
from typing import List, Optional

from .workflow import TDDWorkflow
from .config import get_config, set_config


def read_kata_description(kata_file_path: str) -> str:
    """Read the kata description from a markdown file."""
    try:
        with open(kata_file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: Kata file '{kata_file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading kata file: {e}")
        sys.exit(1)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the agentic-tdd CLI tool."""
    parser = argparse.ArgumentParser(
        description="Multi-agent Test-Driven Development (TDD) CLI tool"
    )
    parser.add_argument(
        "kata_file",
        help="Path to the markdown file containing the code kata description",
    )
    parser.add_argument("--model", help="LLM model to use (e.g. qwen3-coder-plus)")
    parser.add_argument("--provider", help="LLM provider (e.g. perplexity)")
    parser.add_argument("--api-key", help="API key for the LLM provider")
    parser.add_argument(
        "--work-dir",
        default=".",
        help="Working directory for the TDD process (default: current directory)",
    )
    parser.add_argument(
        "--max-cycles", type=int, help="Maximum number of TDD cycles to run"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepare configuration and exit without running workflow",
    )

    # Parse arguments
    parsed_args = parser.parse_args(args)

    # Read the kata description
    kata_description = read_kata_description(parsed_args.kata_file)

    if parsed_args.verbose:
        print(f"Running agentic-tdd with kata file: {parsed_args.kata_file}")
        print(f"Kata description length: {len(kata_description)} characters")

    # Update configuration based on CLI arguments
    config = get_config()

    if parsed_args.model:
        config.default_model = parsed_args.model
        if parsed_args.verbose:
            print(f"Using model: {parsed_args.model}")

    if parsed_args.provider and parsed_args.api_key:
        config.set_api_key(parsed_args.provider, parsed_args.api_key)
        if parsed_args.verbose:
            print(f"Using provider: {parsed_args.provider}")

    if parsed_args.max_cycles:
        config.max_tdd_cycles = parsed_args.max_cycles

    if parsed_args.verbose:
        config.verbose_output = True

    # Set the updated configuration
    set_config(config)

    # Create work directory if it doesn't exist
    work_dir = os.path.abspath(parsed_args.work_dir)
    os.makedirs(work_dir, exist_ok=True)

    if parsed_args.verbose:
        print(f"Working directory: {work_dir}")

    # Dry-run: skip workflow execution
    if parsed_args.dry_run:
        if parsed_args.verbose:
            print("Dry-run mode: Workflow execution skipped.")
        return 0

    # Run the TDD workflow
    try:
        workflow = TDDWorkflow(work_dir, kata_description)
        result = workflow.run()

        if parsed_args.verbose:
            print("\nTDD workflow completed!")
            print(f"Cycles completed: {result['cycles_completed']}")
            print(f"Final agent: {result['final_agent']}")
            print(f"Work directory: {result['work_dir']}")

        return 0
    except Exception as e:
        print(f"Error running TDD workflow: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
