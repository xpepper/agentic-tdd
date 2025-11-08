"""Tests for the Implementer Agent."""

import tempfile
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_implementer_agent_import():
    """Test that the Implementer Agent can be imported."""
    from tdd_agents.implementer import ImplementerAgent
    assert ImplementerAgent is not None


def test_implementer_agent_initialization():
    """Test that the Implementer Agent can be initialized."""
    from tdd_agents.implementer import ImplementerAgent
    
    agent = ImplementerAgent(model_name="gpt-3.5-turbo")
    assert agent is not None
    assert agent.model_name == "gpt-3.5-turbo"


def test_implementer_agent_initialization_with_api_key():
    """Test that the Implementer Agent can be initialized with an API key."""
    from tdd_agents.implementer import ImplementerAgent
    
    agent = ImplementerAgent(model_name="gpt-3.5-turbo", api_key="test-key")
    assert agent is not None
    assert agent.api_key == "test-key"


def test_implement_solution_method():
    """Test the implement_solution method of the Implementer Agent."""
    from tdd_agents.implementer import ImplementerAgent
    
    agent = ImplementerAgent()
    
    # Create a temporary directory to simulate a work directory
    with tempfile.TemporaryDirectory() as temp_dir:
        kata_description = "Write a function that adds two numbers together"
        failing_test = "def test_add_numbers(): assert add_numbers(1, 2) == 3"
        
        result = agent.implement_solution(kata_description, failing_test, temp_dir)
        
        # Check that the result has the expected keys
        assert "implementation_code" in result
        assert "file_path" in result
        assert "kata_description" in result
        assert "failing_test" in result
        
        # Check that the implementation contains expected elements
        assert "add_numbers" in result["implementation_code"]
        
        # Check that the file path is correct
        assert result["file_path"].endswith("implementation.py")
        assert temp_dir in result["file_path"]
        
        # Check that the kata description and failing test are preserved
        assert result["kata_description"] == kata_description
        assert result["failing_test"] == failing_test