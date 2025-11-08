"""Tester Agent that writes failing unit tests."""

import os
from typing import Dict, Any, Optional


class TesterAgent:
    """Agent responsible for writing failing unit tests based on the kata requirements."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """Initialize the Tester Agent."""
        self.model_name = model_name
        self.api_key = api_key
    
    def write_test(self, kata_description: str, work_dir: str) -> Dict[str, Any]:
        """Generate a new failing unit test based on the kata description and current code state.
        
        In a real implementation, this would use an LLM to generate the test.
        For now, this is a placeholder that returns a simple test.
        """
        # In a real implementation, we would:
        # 1. Read existing code and tests from the working directory
        # 2. Use an LLM to generate a new test based on the kata description
        # 3. Determine where to save the test
        
        # For now, return a placeholder test
        placeholder_test = """
import unittest

class TestFromKata(unittest.TestCase):
    def test_placeholder_from_kata(self):
        # This test should fail until the implementer agent makes it pass
        self.fail("Test not yet implemented")
        
if __name__ == '__main__':
    unittest.main()
"""
        
        # Determine where to save the test
        test_file_path = self._determine_test_file_path(work_dir)
        
        return {
            "test_code": placeholder_test.strip(),
            "file_path": test_file_path,
            "kata_description": kata_description
        }
    
    def _read_code_files(self, work_dir: str) -> str:
        """Read all relevant code files from the working directory."""
        code_content = []
        for root, dirs, files in os.walk(work_dir):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', 'node_modules']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            code_content.append(f"File: {file_path}\nContent:\n{content}\n")
                    except Exception:
                        continue  # Skip files that can't be read
        
        return "\n".join(code_content)
    
    def _read_test_files(self, work_dir: str) -> str:
        """Read all existing test files from the working directory."""
        test_content = []
        for root, dirs, files in os.walk(work_dir):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', 'node_modules']]
            
            for file in files:
                if any(test_indicator in file.lower() for test_indicator in ['test', 'spec']):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            test_content.append(f"File: {file_path}\nContent:\n{content}\n")
                    except Exception:
                        continue  # Skip files that can't be read
        
        return "\n".join(test_content)
    
    def _read_git_history(self, work_dir: str) -> str:
        """Read recent git history to understand the sequence of tests implemented."""
        try:
            import subprocess
            # Get the last few git commits to see what tests were added
            result = subprocess.run(
                ['git', 'log', '--oneline', '-10'], 
                cwd=work_dir, 
                capture_output=True, 
                text=True
            )
            return result.stdout if result.returncode == 0 else "No git history available"
        except Exception:
            return "Unable to read git history"
    
    def _determine_test_file_path(self, work_dir: str) -> str:
        """Determine the appropriate path for the new test file."""
        # Look for common test directories
        test_dirs = ['tests', 'test', 'spec', 'specs']
        
        for test_dir in test_dirs:
            test_path = os.path.join(work_dir, test_dir)
            if os.path.exists(test_path):
                return os.path.join(test_path, "test_next.py")
        
        # If no test directory exists, create one
        test_path = os.path.join(work_dir, 'tests')
        os.makedirs(test_path, exist_ok=True)
        return os.path.join(test_path, "test_next.py")
    
    def save_test(self, test_data: Dict[str, Any]) -> str:
        """Save the generated test to the appropriate file."""
        file_path = test_data['file_path']
        test_code = test_data['test_code']
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the test to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        return file_path