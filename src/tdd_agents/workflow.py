"""TDD workflow orchestration for agentic-tdd."""

import os
import subprocess
from typing import Dict, Any, Optional

from .tester import TesterAgent
from .implementer import ImplementerAgent
from .refactorer import RefactorerAgent
from .supervisor import SupervisorAgent
from .config import get_config


class TDDWorkflow:
    """Orchestrates the TDD workflow with the four agents."""
    
    def __init__(self, work_dir: str, kata_description: str):
        """Initialize the TDD workflow."""
        self.work_dir = work_dir
        self.kata_description = kata_description
        self.config = get_config()
        
        # Initialize agents
        self.tester = TesterAgent(
            model_name=self.config.tester_config.model_name,
            api_key=self.config.get_api_key("openai")  # Default to OpenAI for now
        )
        self.implementer = ImplementerAgent(
            model_name=self.config.implementer_config.model_name,
            api_key=self.config.get_api_key("openai")
        )
        self.refactorer = RefactorerAgent(
            model_name=self.config.refactorer_config.model_name,
            api_key=self.config.get_api_key("openai")
        )
        self.supervisor = SupervisorAgent(
            model_name=self.config.supervisor_config.model_name,
            api_key=self.config.get_api_key("openai")
        )
        
        # Initialize workflow state
        self.current_agent = "tester"
        self.cycle_count = 0
        self.max_cycles = self.config.max_tdd_cycles
        self.verbose = self.config.verbose_output
    
    def run(self) -> Dict[str, Any]:
        """Run the complete TDD workflow."""
        if self.verbose:
            print(f"🚀 Starting TDD workflow for kata: {self.kata_description[:50]}...")
            print(f"📁 Working directory: {self.work_dir}")
            print(f"🔄 Max cycles: {self.max_cycles}")
        
        # Initialize git repository if it doesn't exist
        self._initialize_git_repo()
        
        # Main TDD loop
        while self.cycle_count < self.max_cycles:
            self.cycle_count += 1
            
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"🔄 TDD Cycle {self.cycle_count}")
                print(f"🤖 Current agent: {self.current_agent.upper()}")
                print('='*60)
            
            # Run the current agent
            success, result = self._run_current_agent()
            
            if self.verbose:
                status_icon = "✅" if success else "❌"
                print(f"{status_icon} Agent result: {'Success' if success else 'Failure'}")
                if not success:
                    print(f"⚠️  Failure reason: {result.get('failure_reason', 'Unknown')}")
            
            # Have supervisor evaluate progress
            evaluation = self.supervisor.evaluate_progress(
                self.current_agent, success, self.work_dir, **result
            )
            
            if self.verbose:
                print(f"📋 Supervisor: {evaluation['message']}")
            
            # Check if we should continue or stop
            if not success and evaluation["action"] == "stop":
                if self.verbose:
                    print("🛑 Workflow stopped by supervisor.")
                break
            
            # Update current agent based on supervisor evaluation
            self.current_agent = evaluation["next_agent"]
            
            # If we've completed a full cycle (tester -> implementer -> refactorer -> tester)
            if self.current_agent == "tester" and self.cycle_count > 1:
                if self.verbose:
                    print("✅ Completed one full TDD cycle.")
        
        # Return final status
        if self.verbose:
            print(f"\n{'='*60}")
            print("🎯 TDD workflow completed!")
            print(f"📈 Cycles completed: {self.cycle_count}")
            print(f"🤖 Final agent: {self.current_agent}")
            print(f"📁 Work directory: {self.work_dir}")
            print('='*60)
        
        return {
            "success": True,
            "cycles_completed": self.cycle_count,
            "final_agent": self.current_agent,
            "work_dir": self.work_dir
        }
    
    def _run_current_agent(self) -> tuple[bool, Dict[str, Any]]:
        """Run the current agent in the workflow."""
        try:
            if self.current_agent == "tester":
                return self._run_tester_agent()
            elif self.current_agent == "implementer":
                return self._run_implementer_agent()
            elif self.current_agent == "refactorer":
                return self._run_refactorer_agent()
            else:
                # Default to tester if unknown agent
                self.current_agent = "tester"
                return self._run_tester_agent()
        except Exception as e:
            return False, {"failure_reason": f"Agent execution error: {str(e)}"}
    
    def _run_tester_agent(self) -> tuple[bool, Dict[str, Any]]:
        """Run the tester agent to write a failing test."""
        if self.verbose:
            print("📝 Tester Agent: Writing a new failing test...")
        
        # Generate a new test
        test_data = self.tester.write_test(self.kata_description, self.work_dir)
        
        # Save the test
        test_file_path = self.tester.save_test(test_data)
        
        if self.verbose:
            print(f"📝 Tester Agent: Wrote test to {test_file_path}")
        
        # Run the test to verify it fails
        if self.verbose:
            print("🧪 Tester Agent: Running test to verify it fails...")
        test_result = self._run_tests()
        
        if test_result["success"]:
            # Test passed, which means it's not a proper failing test
            if self.verbose:
                print("❌ Tester Agent: Test already passes - not a proper failing test")
            return False, {
                "failure_reason": "Test already passes - not a proper failing test",
                "test_file": test_file_path,
                "test_result": test_result
            }
        else:
            # Test failed, which is what we want for a proper TDD cycle
            if self.verbose:
                print("✅ Tester Agent: Test correctly fails - ready for implementation")
            if self.config.enable_git_staging:
                self._stage_file(test_file_path)
            
            return True, {
                "test_file": test_file_path,
                "test_result": test_result
            }
    
    def _run_implementer_agent(self) -> tuple[bool, Dict[str, Any]]:
        """Run the implementer agent to make the test pass."""
        if self.verbose:
            print("🔨 Implementer Agent: Making the test pass...")
        
        # Get the most recently added test file
        test_file = self._find_latest_test_file()
        
        if not test_file:
            if self.verbose:
                print("❌ Implementer Agent: No test file found to implement against")
            return False, {"failure_reason": "No test file found to implement against"}
        
        if self.verbose:
            print(f"📖 Implementer Agent: Reading test from {test_file}")
        
        # Read the test file content
        try:
            with open(test_file, 'r') as f:
                test_content = f.read()
        except Exception as e:
            if self.verbose:
                print(f"❌ Implementer Agent: Could not read test file: {str(e)}")
            return False, {"failure_reason": f"Could not read test file: {str(e)}"}
        
        # Generate implementation
        implementation_data = self.implementer.implement_solution(
            self.kata_description, test_content, self.work_dir
        )
        
        # Save the implementation
        implementation_file_path = self.implementer.save_implementation(implementation_data)
        
        if self.verbose:
            print(f"🔨 Implementer Agent: Wrote implementation to {implementation_file_path}")
        
        # Run the tests to verify they now pass
        if self.verbose:
            print("🧪 Implementer Agent: Running tests to verify implementation...")
        test_result = self.implementer.run_tests(self.work_dir)
        
        if test_result["success"]:
            # Tests pass, implementation successful
            if self.verbose:
                print("✅ Implementer Agent: All tests now pass!")
            if self.config.enable_git_staging:
                self._stage_file(implementation_file_path)
                self._commit_changes(f"Implement solution for test in {os.path.basename(test_file)}")
            
            return True, {
                "implementation_file": implementation_file_path,
                "test_result": test_result
            }
        else:
            # Tests still fail, implementation unsuccessful
            if self.verbose:
                print("❌ Implementer Agent: Tests still failing after implementation")
            return False, {
                "failure_reason": "Tests still failing after implementation",
                "implementation_file": implementation_file_path,
                "test_result": test_result
            }
    
    def _run_refactorer_agent(self) -> tuple[bool, Dict[str, Any]]:
        """Run the refactorer agent to improve code quality."""
        if self.verbose:
            print("🔄 Refactorer Agent: Improving code quality...")
        
        # Run tests first to ensure they pass before refactoring
        if self.verbose:
            print("🧪 Refactorer Agent: Running tests before refactoring...")
        test_result = self.refactorer.run_tests(self.work_dir)
        
        if not test_result["success"]:
            if self.verbose:
                print("❌ Refactorer Agent: Tests failing before refactoring - cannot proceed")
            return False, {
                "failure_reason": "Tests failing before refactoring - cannot proceed",
                "test_result": test_result
            }
        
        # Refactor the code
        refactor_data = self.refactorer.refactor_code(self.work_dir, "Improve code quality after implementation")
        
        # Apply the refactoring
        self.refactorer.apply_refactoring(refactor_data)
        
        if self.verbose:
            print("🔄 Refactorer Agent: Applied code improvements")
        
        # Run tests again to ensure they still pass after refactoring
        if self.verbose:
            print("🧪 Refactorer Agent: Running tests after refactoring...")
        test_result_after = self.refactorer.run_tests(self.work_dir)
        
        if test_result_after["success"]:
            # Tests still pass, refactoring successful
            if self.verbose:
                print("✅ Refactorer Agent: All tests pass after refactoring!")
            if self.config.enable_git_staging:
                self._commit_changes("Refactor code for improved quality")
            
            return True, {
                "refactor_data": refactor_data,
                "test_result": test_result_after
            }
        else:
            # Tests now fail, refactoring broke something
            if self.verbose:
                print("❌ Refactorer Agent: Tests failing after refactoring")
            return False, {
                "failure_reason": "Tests failing after refactoring",
                "refactor_data": refactor_data,
                "test_result": test_result_after
            }
    
    def _run_tests(self) -> Dict[str, Any]:
        """Run tests in the work directory."""
        try:
            # Try running tests with pytest first
            result = subprocess.run(
                ['python', '-m', 'pytest', '-v'], 
                cwd=self.work_dir, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Test execution timed out",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def _initialize_git_repo(self) -> None:
        """Initialize a git repository in the work directory if it doesn't exist."""
        try:
            # Check if git repo already exists
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'], 
                cwd=self.work_dir, 
                capture_output=True
            )
        except Exception:
            # Git repo doesn't exist, initialize it
            try:
                subprocess.run(
                    ['git', 'init'], 
                    cwd=self.work_dir, 
                    capture_output=True
                )
                # Set up initial commit
                subprocess.run(
                    ['git', 'add', '.'], 
                    cwd=self.work_dir, 
                    capture_output=True
                )
                subprocess.run(
                    ['git', 'commit', '-m', 'Initial commit'], 
                    cwd=self.work_dir, 
                    capture_output=True
                )
            except Exception:
                pass  # If git init fails, continue without it
    
    def _stage_file(self, file_path: str) -> None:
        """Stage a file in git."""
        try:
            subprocess.run(
                ['git', 'add', file_path], 
                cwd=self.work_dir, 
                capture_output=True
            )
        except Exception:
            pass  # If git staging fails, continue without it
    
    def _commit_changes(self, message: str) -> None:
        """Commit changes in git."""
        try:
            subprocess.run(
                ['git', 'commit', '-m', message], 
                cwd=self.work_dir, 
                capture_output=True
            )
        except Exception:
            pass  # If git commit fails, continue without it
    
    def _find_latest_test_file(self) -> Optional[str]:
        """Find the most recently created test file."""
        test_files = []
        
        for root, dirs, files in os.walk(self.work_dir):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', 'node_modules']]
            
            for file in files:
                if any(test_indicator in file.lower() for test_indicator in ['test', 'spec']):
                    file_path = os.path.join(root, file)
                    test_files.append(file_path)
        
        if not test_files:
            return None
        
        # Return the most recently modified test file
        return max(test_files, key=os.path.getmtime)