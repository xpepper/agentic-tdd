"""Implementer Agent that makes tests pass."""

import os
import subprocess
from typing import Dict, Any, Optional


class ImplementerAgent:
    """Agent responsible for implementing code to make the failing tests pass."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """Initialize the Implementer Agent."""
        self.model_name = model_name
        self.api_key = api_key
    
    def implement_solution(self, kata_description: str, failing_test: str, work_dir: str) -> Dict[str, Any]:
        """Implement the minimal code changes needed to make the failing test pass.
        
        In a real implementation, this would use an LLM to generate the implementation.
        For now, this is a placeholder that returns a simple implementation.
        """
        # In a real implementation, we would:
        # 1. Read the failing test and existing code
        # 2. Use an LLM to generate the minimal implementation needed
        # 3. Determine which files to modify
        
        # For now, return a placeholder implementation
        placeholder_implementation = '''
def add_numbers(a, b):
    """Add two numbers together."""
    return a + b
'''
        
        # Determine where to save the implementation
        implementation_file_path = self._determine_implementation_file_path(work_dir)
        
        return {
            "implementation_code": placeholder_implementation.strip(),
            "file_path": implementation_file_path,
            "kata_description": kata_description,
            "failing_test": failing_test
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
    
    def _find_failing_test_file(self, work_dir: str) -> Optional[str]:
        """Find the file containing the failing test."""
        for root, dirs, files in os.walk(work_dir):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', 'node_modules']]
            
            for file in files:
                if any(test_indicator in file.lower() for test_indicator in ['test', 'spec']):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Check if this file contains test methods that might be failing
                            if 'def test_' in content or 'unittest' in content:
                                return file_path
                    except Exception:
                        continue  # Skip files that can't be read
        
        return None
    
    def _determine_implementation_file_path(self, work_dir: str) -> str:
        """Determine the appropriate path for the implementation file."""
        # Look for common source directories
        src_dirs = ['src', 'lib', 'source', 'app', '']
        
        for src_dir in src_dirs:
            if src_dir == '':
                src_path = work_dir
            else:
                src_path = os.path.join(work_dir, src_dir)
            
            if os.path.exists(src_path):
                return os.path.join(src_path, "implementation.py")
        
        # If no source directory exists, use the work directory root
        return os.path.join(work_dir, "implementation.py")
    
    def save_implementation(self, implementation_data: Dict[str, Any]) -> str:
        """Save the generated implementation to the appropriate file."""
        file_path = implementation_data['file_path']
        implementation_code = implementation_data['implementation_code']
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the implementation to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(implementation_code)
        
        return file_path
    
    def run_tests(self, work_dir: str) -> Dict[str, Any]:
        """Run the tests to verify that they now pass."""
        try:
            # Try running tests with pytest first
            result = subprocess.run(
                ['python', '-m', 'pytest', '-v'], 
                cwd=work_dir, 
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