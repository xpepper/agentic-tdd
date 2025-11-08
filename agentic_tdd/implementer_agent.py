"""
Implementer Agent module.
Responsible for making minimal changes to code to make tests pass.
"""
from typing import Dict, Any
from .core import Agent, AgentException
from .llm import LLMProvider, create_implementer_prompt
from .test_runner import TestRunner
from .logger import get_agent_logger
import os
from pathlib import Path


class ImplementerAgent(Agent):
    """Agent responsible for implementing code to make tests pass."""
    
    def __init__(self, work_dir: str, kata_description: str, config):
        super().__init__("Implementer", work_dir, kata_description, config)
        try:
            self.llm_provider = LLMProvider(
                model=config.model,
                provider=config.provider,
                api_key=config.api_key,
                base_url=config.base_url
            )
            self.test_runner = TestRunner(self.work_dir)
            self.logger.info("Implementer agent initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Implementer agent: {str(e)}")
            raise AgentException(f"Implementer agent initialization failed: {str(e)}")
    
    def execute(self) -> Dict[str, Any]:
        """Execute the implementer agent's role: make tests pass."""
        try:
            self.logger.info("Starting implementer agent execution")
            print(f"{self.name}: Implementing code to make tests pass...")
            
            result = self._implement_code()
            
            # Verify that all tests now pass
            tests_pass = self._verify_tests_pass()
            
            message = f"Implementer agent completed. All tests pass: {tests_pass}"
            self.logger.info(message)
            
            return {
                'success': True,
                'implementation_files': result['files'],
                'tests_pass': tests_pass,
                'message': message
            }
        except Exception as e:
            error_msg = f"Implementer agent execution failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'implementation_files': [],
                'tests_pass': False,
                'message': error_msg
            }
    
    def _implement_code(self) -> Dict[str, list]:
        """Implement code based on the failing tests using LLM."""
        try:
            self.logger.debug("Reading failing test for implementation context")
            # Read the failing test to understand what needs to be implemented
            failing_test = self._read_failing_test()
            
            self.logger.debug("Reading existing code for implementation context")
            # Read existing code to provide context
            existing_code = self._read_existing_code()
            
            self.logger.debug("Creating LLM prompt for implementation")
            # Create the prompt for the LLM
            prompt = create_implementer_prompt(
                kata_description=self.kata_content,
                failing_test=failing_test,
                existing_code=existing_code
            )
            
            self.logger.debug("Generating implementation using LLM")
            # Generate the implementation using LLM
            impl_content = self.llm_provider.generate_code(prompt, language="python")
            
            # Create an implementation file name
            impl_file_name = "calculator.py"  # Default name, could be more dynamic
            impl_file = self.work_dir / impl_file_name
            
            self.logger.debug(f"Writing generated implementation to file: {impl_file}")
            # Write the implementation to file
            with open(impl_file, 'w', encoding='utf-8') as f:
                f.write(impl_content)
            
            self.logger.info(f"Implementation file created successfully: {impl_file}")
            return {
                'files': [str(impl_file)]
            }
        except Exception as e:
            self.logger.error(f"Error implementing code: {str(e)}")
            raise AgentException(f"Failed to implement code: {str(e)}")
    
    def _read_failing_test(self) -> str:
        """Read the most recently added test to understand what needs to be implemented."""
        try:
            test_files = list(self.work_dir.rglob("*test*.py"))
            if not test_files:
                self.logger.warning("No test files found")
                return "No test files found."
            
            # Get the most recent test file
            latest_test_file = max(test_files, key=lambda f: f.stat().st_mtime)
            
            try:
                with open(latest_test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.logger.debug(f"Read failing test from {latest_test_file}")
                    return content
            except Exception as e:
                self.logger.warning(f"Could not read test file {latest_test_file}: {str(e)}")
                return "Could not read test file."
        except Exception as e:
            self.logger.error(f"Error reading failing test: {str(e)}")
            return "Error reading test files."
    
    def _read_existing_code(self) -> str:
        """Read existing implementation code to provide context."""
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
            self.logger.error(f"Error reading existing code: {str(e)}")
            return ""
    
    def _verify_tests_pass(self) -> bool:
        """Verify that all tests now pass."""
        try:
            self.logger.debug("Verifying all tests pass")
            # Use the test runner to check if all tests pass
            return self.test_runner.run_test_to_verify_pass()
        except Exception as e:
            self.logger.error(f"Error verifying tests: {str(e)}")
            # If we can't run the tests, assume they don't pass
            return False

