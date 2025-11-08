"""Refactorer Agent that improves code quality."""

import os
import subprocess
from typing import Dict, Any, Optional


class RefactorerAgent:
    """Agent responsible for improving code quality after all tests pass."""

    def __init__(
        self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None
    ):
        """Initialize the Refactorer Agent."""
        self.model_name = model_name
        self.api_key = api_key

    def refactor_code(
        self, work_dir: str, refactor_reason: str = "General code quality improvement"
    ) -> Dict[str, Any]:
        """Refactor the code to improve readability, modularity, and maintainability.

        In a real implementation, this would use an LLM to generate refactored code.
        For now, this is a placeholder that returns the same code with basic improvements.
        """
        # In a real implementation, we would:
        # 1. Read all code files to understand the codebase
        # 2. Use an LLM to suggest refactoring improvements
        # 3. Apply the refactoring while ensuring all tests still pass

        # Read existing code
        all_code_files = self._get_all_code_files(work_dir)

        refactor_results = {}

        for file_path, original_content in all_code_files.items():
            # For now, return the original content (placeholder implementation)
            # In a real implementation, this would contain refactored code
            refactor_results[file_path] = {
                "original_content": original_content,
                "refactored_content": original_content,  # Placeholder: no actual refactoring yet
                "refactor_reason": refactor_reason,
            }

        return {
            "refactor_results": refactor_results,
            "refactor_reason": refactor_reason,
            "work_dir": work_dir,
        }

    def _get_all_code_files(self, work_dir: str) -> Dict[str, str]:
        """Get all code files in the working directory with their content."""
        code_files = {}

        for root, dirs, files in os.walk(work_dir):
            # Skip common non-code directories
            dirs[:] = [
                d
                for d in dirs
                if d not in [".git", "__pycache__", ".venv", "venv", "node_modules"]
            ]

            for file in files:
                if file.endswith(
                    (".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs")
                ):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            code_files[file_path] = content
                    except Exception:
                        continue  # Skip files that can't be read

        return code_files

    def apply_refactoring(self, refactor_data: Dict[str, Any]) -> bool:
        """Apply the refactoring changes to the codebase."""
        refactor_results = refactor_data.get("refactor_results", {})

        for file_path, refactored_data in refactor_results.items():
            refactored_content = refactored_data["refactored_content"]

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Write the refactored content to the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(refactored_content)

        return True

    def run_tests(self, work_dir: str) -> Dict[str, Any]:
        """Run the tests to verify that they still pass after refactoring."""
        try:
            # Try running tests with pytest first
            result = subprocess.run(
                ["python", "-m", "pytest", "-v"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Test execution timed out",
                "returncode": -1,
            }
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}
