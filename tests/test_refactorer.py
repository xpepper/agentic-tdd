"""Tests for the Refactorer Agent."""

import tempfile
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_refactorer_agent_import():
    """Test that the Refactorer Agent can be imported."""
    from tdd_agents.refactorer import RefactorerAgent

    assert RefactorerAgent is not None


def test_refactorer_agent_initialization():
    """Test that the Refactorer Agent can be initialized."""
    from tdd_agents.refactorer import RefactorerAgent

    agent = RefactorerAgent(model_name="gpt-3.5-turbo")
    assert agent is not None
    assert agent.model_name == "gpt-3.5-turbo"


def test_refactorer_agent_initialization_with_api_key():
    """Test that the Refactorer Agent can be initialized with an API key."""
    from tdd_agents.refactorer import RefactorerAgent

    agent = RefactorerAgent(model_name="gpt-3.5-turbo", api_key="test-key")
    assert agent is not None
    assert agent.api_key == "test-key"


def test_refactor_code_method():
    """Test the refactor_code method of the Refactorer Agent."""
    from tdd_agents.refactorer import RefactorerAgent

    agent = RefactorerAgent()

    # Create a temporary directory to simulate a work directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple Python file to refactor
        test_file_path = os.path.join(temp_dir, "test_module.py")
        with open(test_file_path, "w") as f:
            f.write("def add(a, b):\n    return a + b\n")

        refactor_reason = "Improve function naming"
        result = agent.refactor_code(temp_dir, refactor_reason)

        # Check that the result has the expected keys
        assert "refactor_results" in result
        assert "refactor_reason" in result
        assert "work_dir" in result

        # Check that the refactor results contain the test file
        assert test_file_path in result["refactor_results"]

        # Check that the refactor reason is preserved
        assert result["refactor_reason"] == refactor_reason

        # Check that the work directory is correct
        assert result["work_dir"] == temp_dir
