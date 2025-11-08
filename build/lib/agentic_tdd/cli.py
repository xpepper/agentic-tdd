"""
CLI module for agentic-tdd.
"""
import argparse
import os
import sys
from typing import List, Optional
from .core import AgentConfig
from .supervisor_agent import SupervisorAgent


def parse_arguments(args: List[str]) -> argparse.Namespace:
    """
    Parse command line arguments for agentic-tdd.
    
    Args:
        args: Command line arguments
        
    Returns:
        Parsed arguments as a Namespace object
    """
    parser = argparse.ArgumentParser(
        description="Multi-Agent Test-Driven Development CLI Tool"
    )
    
    parser.add_argument(
        "kata_description",
        help="Path to the kata description file (markdown format)"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-4",
        help="LLM model to use (default: gpt-4)"
    )
    
    parser.add_argument(
        "--provider",
        default="openai",
        help="LLM provider to use (default: openai)"
    )
    
    parser.add_argument(
        "--api-key",
        help="API key for the LLM provider (can also use environment variables)"
    )
    
    parser.add_argument(
        "--work-dir",
        required=True,
        help="Working directory for the TDD process"
    )
    
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=10,
        help="Maximum number of TDD cycles to perform (default: 10)"
    )
    
    return parser.parse_args(args)

def main() -> None:
    """Main entry point for the CLI."""
    args = parse_arguments(sys.argv[1:])
    
    # Validate kata description file exists
    if not os.path.exists(args.kata_description):
        print(f"Error: Kata description file not found: {args.kata_description}")
        sys.exit(1)
    
    # Create work directory if it doesn't exist
    os.makedirs(args.work_dir, exist_ok=True)
    
    print(f"Agentic TDD starting with:")
    print(f"  Kata description: {args.kata_description}")
    print(f"  Model: {args.model}")
    print(f"  Provider: {args.provider}")
    print(f"  Work directory: {args.work_dir}")
    print(f"  Max cycles: {args.max_cycles}")
    
    # Create agent configuration
    config = AgentConfig(
        model=args.model,
        provider=args.provider,
        api_key=args.api_key,
        max_cycles=args.max_cycles
    )
    
    # Start the supervisor agent which will coordinate the process
    supervisor = SupervisorAgent(args.work_dir, args.kata_description, config)
    result = supervisor.execute()
    
    print(f"\nAgentic TDD completed: {result['message']}")