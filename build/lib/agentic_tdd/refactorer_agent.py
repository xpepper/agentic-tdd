"""
Refactorer Agent module.
Responsible for improving code quality while keeping all tests passing.
"""
from typing import Dict, Any
from .core import Agent, AgentException
from .llm import LLMProvider, create_refactorer_prompt
from .test_runner import TestRunner
from .logger import get_agent_logger
import os
from pathlib import Path


class RefactorerAgent(Agent):
    """Agent responsible for refactoring code to improve quality."""
    
    def __init__(self, work_dir: str, kata_description: str, config):
        super().__init__("Refactorer", work_dir, kata_description, config)
        try:
            self.llm_provider = LLMProvider(
                model=config.model,
                provider=config.provider,
                api_key=config.api_key
            )
            self.test_runner = TestRunner(self.work_dir)
            self.logger.info("Refactorer agent initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Refactorer agent: {str(e)}")
            raise AgentException(f"Refactorer agent initialization failed: {str(e)}")
    
    def execute(self) -> Dict[str, Any]:
        """Execute the refactorer agent's role: improve code quality."""
        try:
            self.logger.info("Starting refactorer agent execution")
            print(f"{self.name}: Analyzing code for potential improvements...")
            
            result = self._refactor_code()
            
            # Verify that all tests still pass after refactoring
            tests_pass = self._verify_tests_pass()
            
            message = f"Refactorer agent completed. All tests still pass: {tests_pass}"
            self.logger.info(message)
            
            return {
                'success': True,
                'refactored_files': result['files'],
                'tests_pass': tests_pass,
                'message': message
            }
        except Exception as e:
            error_msg = f"Refactorer agent execution failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'refactored_files': [],
                'tests_pass': False,
                'message': error_msg
            }
    
    def _refactor_code(self) -> Dict[str, list]:
        """Refactor code based on quality guidelines using LLM."""
        try:
            self.logger.debug("Reading existing code for refactoring")
            # Read existing code to refactor
            code_to_refactor = self._read_code_to_refactor()
            
            self.logger.debug("Reading existing tests for reference")
            # Read existing tests for reference
            existing_tests = self._read_existing_tests()
            
            self.logger.debug("Creating LLM prompt for refactoring")
            # Create the prompt for the LLM
            prompt = create_refactorer_prompt(
                kata_description=self.kata_content,
                code_to_refactor=code_to_refactor,
                existing_tests=existing_tests
            )
            
            self.logger.debug("Generating refactored code using LLM")
            # Generate the refactored code using LLM
            refactored_content = self.llm_provider.generate_code(prompt, language="python")
            
            # Find files to refactor (for now, just refactor the main implementation file)
            impl_files = [f for f in self.work_dir.rglob("*.py") if "test" not in f.name.lower()]
            if not impl_files:
                self.logger.warning("No implementation files found to refactor")
                return {'files': []}
            
            # Refactor the most recent implementation file
            impl_file = max(impl_files, key=lambda f: f.stat().st_mtime)
            
            self.logger.debug(f"Writing refactored code to file: {impl_file}")
            # Write the refactored code to file
            with open(impl_file, 'w', encoding='utf-8') as f:
                f.write(refactored_content)
            
            self.logger.info(f"Refactored file successfully: {impl_file}")
            return {
                'files': [str(impl_file)]
            }
        except Exception as e:
            self.logger.error(f"Error during refactoring: {str(e)}")
            raise AgentException(f"Failed to refactor code: {str(e)}")
    
    def _read_code_to_refactor(self) -> str:
        """Read existing implementation code to refactor."""
        try:
            code_files = []
            for file_path in self.work_dir.rglob("*.py"):
                if "test" not in file_path.name.lower():  # Skip test files
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            code_files.append(f"File: {file_path.name}\n{content}\n")
                    except Exception as e:
                        self.logger.warning(f"Could not read file {file_path}: {str(e)}")
                        continue  # Skip files that can't be read
            
            return "\n".join(code_files)
        except Exception as e:
            self.logger.error(f"Error reading code to refactor: {str(e)}")
            return ""
    
    def _read_existing_tests(self) -> str:
        """Read existing test code for reference."""
        try:
            test_files = []
            for file_path in self.work_dir.rglob("*test*.py"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        test_files.append(f"File: {file_path.name}\n{content}\n")
                except Exception as e:
                    self.logger.warning(f"Could not read test file {file_path}: {str(e)}")
                    continue  # Skip files that can't be read
            
            return "\n".join(test_files)
        except Exception as e:
            self.logger.error(f"Error reading existing tests: {str(e)}")
            return ""
    
    def _verify_tests_pass(self) -> bool:
        """Verify that all tests still pass after refactoring."""
        try:
            self.logger.debug("Verifying tests still pass after refactoring")
            # Use the test runner to check if all tests still pass
            return self.test_runner.run_test_to_verify_pass()
        except Exception as e:
            self.logger.error(f"Error verifying tests after refactoring: {str(e)}")
            # If we can't run the tests, assume they don't pass
            return False

