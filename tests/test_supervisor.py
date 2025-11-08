"""Tests for the Supervisor Agent."""

import tempfile
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_supervisor_agent_import():
    """Test that the Supervisor Agent can be imported."""
    from tdd_agents.supervisor import SupervisorAgent
    assert SupervisorAgent is not None


def test_supervisor_agent_initialization():
    """Test that the Supervisor Agent can be initialized."""
    from tdd_agents.supervisor import SupervisorAgent
    
    agent = SupervisorAgent(model_name="gpt-3.5-turbo")
    assert agent is not None
    assert agent.model_name == "gpt-3.5-turbo"
    assert agent.agent_penalties == {"tester": 0, "implementer": 0, "refactorer": 0}


def test_supervisor_agent_initialization_with_api_key():
    """Test that the Supervisor Agent can be initialized with an API key."""
    from tdd_agents.supervisor import SupervisorAgent
    
    agent = SupervisorAgent(model_name="gpt-3.5-turbo", api_key="test-key")
    assert agent is not None
    assert agent.api_key == "test-key"


def test_evaluate_progress_success():
    """Test the evaluate_progress method with a successful agent."""
    from tdd_agents.supervisor import SupervisorAgent
    
    agent = SupervisorAgent()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        result = agent.evaluate_progress("tester", True, temp_dir)
        
        # Check that the result has the expected keys
        assert "success" in result
        assert "next_agent" in result
        assert "message" in result
        assert "action" in result
        
        # Check that the result indicates success
        assert result["success"]
        assert result["action"] == "continue"
        
        # Check that the next agent is correct (tester -> implementer)
        assert result["next_agent"] == "implementer"


def test_evaluate_progress_failure_tester():
    """Test the evaluate_progress method with a failing tester agent."""
    from tdd_agents.supervisor import SupervisorAgent
    
    agent = SupervisorAgent()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        result = agent.evaluate_progress("tester", False, temp_dir, failure_reason="Test already passes")
        
        # Check that the result has the expected keys
        assert "success" in result
        assert "next_agent" in result
        assert "message" in result
        assert "action" in result
        assert "failure_reason" in result
        
        # Check that the result indicates failure
        assert not result["success"]
        assert result["failure_reason"] == "Test already passes"


def test_get_agent_status():
    """Test getting agent status."""
    from tdd_agents.supervisor import SupervisorAgent
    
    agent = SupervisorAgent()
    
    # Initially all penalties should be zero
    status = agent.get_agent_status()
    assert status == {"tester": 0, "implementer": 0, "refactorer": 0}
    
    # Test applying a penalty
    agent._apply_penalty("tester", "Failed to write failing test")
    status = agent.get_agent_status()
    assert status["tester"] == 1