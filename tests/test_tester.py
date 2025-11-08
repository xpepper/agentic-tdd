"""Tests for the Tester Agent."""

import tempfile
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_tester_agent_import():
    """Test that the Tester Agent can be imported."""
    from tdd_agents.tester import TesterAgent
    assert TesterAgent is not None


def test_tester_agent_initialization():
    """Test that the Tester Agent can be initialized."""
    from tdd_agents.tester import TesterAgent
    
    agent = TesterAgent(model_name="gpt-3.5-turbo")
    assert agent is not None
    assert agent.model_name == "gpt-3.5-turbo"


def test_tester_agent_initialization_with_api_key():
    """Test that the Tester Agent can be initialized with an API key."""
    from tdd_agents.tester import TesterAgent
    
    agent = TesterAgent(model_name="gpt-3.5-turbo", api_key="test-key")
    assert agent is not None
    assert agent.api_key == "test-key"


def test_write_test_method():
    """Test the write_test method of the Tester Agent."""
    from tdd_agents.tester import TesterAgent
    
    agent = TesterAgent()
    
    # Create a temporary directory to simulate a work directory
    with tempfile.TemporaryDirectory() as temp_dir:
        kata_description = "Write a function that adds two numbers together"
        
        result = agent.write_test(kata_description, temp_dir)
        
        # Check that the result has the expected keys
        assert "test_code" in result
        assert "file_path" in result
        assert "kata_description" in result
        
        # Check that the test code contains expected elements
        assert "unittest" in result["test_code"]
        assert "TestFromKata" in result["test_code"]
        assert "test_placeholder_from_kata" in result["test_code"]
        
        # Check that the file path is correct
        assert result["file_path"].endswith("test_next.py")
        assert temp_dir in result["file_path"]
        
        # Check that the kata description is preserved
        assert result["kata_description"] == kata_description