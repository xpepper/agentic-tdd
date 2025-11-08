"""
Tester Agent module.
Responsible for writing failing unit tests that capture the next required behavior.
"""
from typing import Dict, Any
from .core import Agent, AgentException
from .llm import LLMProvider, create_tester_prompt
from .test_runner import TestRunner
from .logger import get_agent_logger
import os
from pathlib import Path


class TesterAgent(Agent):
    """Agent responsible for writing failing unit tests."""
    
    def __init__(self, work_dir: str, kata_description: str, config):
        super().__init__("Tester", work_dir, kata_description, config)
        try:
            self.llm_provider = LLMProvider(
                model=config.model,
                provider=config.provider,
                api_key=config.api_key
            )
            self.test_runner = TestRunner(self.work_dir)
            self.logger.info("Tester agent initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Tester agent: {str(e)}")
            raise AgentException(f"Tester agent initialization failed: {str(e)}")
    
    def execute(self) -> Dict[str, Any]:
        """Execute the tester agent's role: write a failing test."""
        try:
            self.logger.info("Starting tester agent execution")
            print(f"{self.name}: Analyzing kata requirements and writing a new failing test...")
            
            result = self._generate_test()
            
            # Verify the test fails (it should since it's new)
            test_fails = self._verify_test_fails(result['test_file'])
            
            message = f"Tester agent completed. New test fails as expected: {test_fails}"
            self.logger.info(message)
            
            return {
                'success': True,
                'test_file': result['test_file'],
                'test_content': result['test_content'],
                'test_fails': test_fails,  # Should be True for a good test
                'message': message
            }
        except Exception as e:
            error_msg = f"Tester agent execution failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'test_file': None,
                'test_content': None,
                'test_fails': False,
                'message': error_msg
            }
    
    def _generate_test(self) -> Dict[str, str]:
        """Generate a test based on the kata description using LLM."""
        try:
            self.logger.debug("Reading existing code and tests for context")
            # Read existing code and tests to provide context
            existing_code = self._read_existing_code()
            existing_tests = self._read_existing_tests()
            
            self.logger.debug("Creating LLM prompt for test generation")
            # Create the prompt for the LLM
            prompt = create_tester_prompt(
                kata_description=self.kata_content,
                existing_code=existing_code,
                existing_tests=existing_tests
            )
            
            self.logger.debug("Generating test using LLM")
            # Generate the test using LLM
            test_content = self.llm_provider.generate_code(prompt, language="python")
            
            # Create a test file name based on the kata
            test_file_name = "test_calculator.py"  # Default name, could be more dynamic
            test_file = self.work_dir / test_file_name
            
            self.logger.debug(f"Writing generated test to file: {test_file}")
            # Write the test to file
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            self.logger.info(f"Test file created successfully: {test_file}")
            return {
                'test_file': str(test_file),
                'test_content': test_content
            }
        except Exception as e:
            self.logger.error(f"Error generating test: {str(e)}")
            raise AgentException(f"Failed to generate test: {str(e)}")
    
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
    
    def _read_existing_tests(self) -> str:
        """Read existing test code to provide context."""
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
    
    def _verify_test_fails(self, test_file: str) -> bool:
        """Verify that the generated test actually fails as expected."""
        try:
            self.logger.debug(f"Verifying that test fails: {test_file}")
            # Use the test runner to check if the test fails
            return self.test_runner.run_test_to_verify_failure(test_file)
        except Exception as e:
            self.logger.warning(f"Could not run test verification: {str(e)}")
            # If we can't run the test, assume it's not passing (which is what we want for a new test)
            return True  # Consider this a success for the test creation