"""Tests for the TDD workflow."""

import tempfile
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_workflow_import():
    """Test that the TDD Workflow can be imported."""
    from tdd_agents.workflow import TDDWorkflow
    assert TDDWorkflow is not None


def test_workflow_initialization():
    """Test that the TDD Workflow can be initialized."""
    from tdd_agents.workflow import TDDWorkflow
    
    with tempfile.TemporaryDirectory() as temp_dir:
        kata_description = "Write a function that adds two numbers together"
        
        workflow = TDDWorkflow(temp_dir, kata_description)
        assert workflow is not None
        assert workflow.work_dir == temp_dir
        assert workflow.kata_description == kata_description
        assert workflow.current_agent == "tester"
        assert workflow.cycle_count == 0


def test_workflow_agents_initialized():
    """Test that all agents are initialized in the workflow."""
    from tdd_agents.workflow import TDDWorkflow
    
    with tempfile.TemporaryDirectory() as temp_dir:
        kata_description = "Write a function that adds two numbers together"
        
        workflow = TDDWorkflow(temp_dir, kata_description)
        
        # Check that all agents are initialized
        assert workflow.tester is not None
        assert workflow.implementer is not None
        assert workflow.refactorer is not None
        assert workflow.supervisor is not None