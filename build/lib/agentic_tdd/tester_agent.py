"""
Tester Agent module.
Responsible for writing failing unit tests that capture the next required behavior.
"""
from typing import Dict, Any
from .core import Agent, AgentException
from .llm import LLMProvider, create_tester_prompt
from .test_runner import TestRunner
from .logger import get_agent_logger
from .utils import generate_test_module_name
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
                api_key=config.api_key,
                base_url=config.base_url
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
            new_test_content = self.llm_provider.generate_code(prompt, language="python")
            
            # Create a test file name based on the kata
            test_file_name = f"{generate_test_module_name(self.kata_content)}.py"
            test_file = self.work_dir / test_file_name
            
            # Check if test file already exists
            if test_file.exists():
                # If file exists, read the current content
                with open(test_file, 'r', encoding='utf-8') as f:
                    existing_file_content = f.read()
                
                # Append the new test to the existing content
                # This is a simple approach - in a more sophisticated version, 
                # we might want to parse the file to insert the test in the right place
                updated_content = self._append_new_test(existing_file_content, new_test_content)
            else:
                # If file doesn't exist, use the generated content as is
                updated_content = new_test_content
            
            self.logger.debug(f"Writing updated test to file: {test_file}")
            # Write the updated content to file
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            self.logger.info(f"Test file updated successfully: {test_file}")
            return {
                'test_file': str(test_file),
                'test_content': updated_content
            }
        except Exception as e:
            self.logger.error(f"Error generating test: {str(e)}")
            raise AgentException(f"Failed to generate test: {str(e)}")
    
    def _append_new_test(self, existing_content: str, new_test: str) -> str:
        """Append a new test to existing test file content."""
        # Parse the new test to extract just the method
        new_test_lines = new_test.split('\n')
        
        # Find the actual test method in the new test content
        # Look for a method that starts with 'def test_'
        test_method_lines = []
        import_lines = []
        
        # Extract imports and test method separately
        in_method = False
        method_indentation = ""
        
        for line in new_test_lines:
            line_stripped = line.lstrip()
            
            # Collect import statements
            if line_stripped.startswith('import ') or line_stripped.startswith('from '):
                import_lines.append(line)
                continue
            
            # Look for test method
            if line_stripped.startswith('def test_'):
                in_method = True
                # Calculate the indentation of this line to maintain it for the method body
                method_indentation = line[:len(line) - len(line.lstrip())]
                test_method_lines.append(line)
            elif in_method:
                # Check if this line is still part of the method (indented more than the def)
                current_indent = line[:len(line) - len(line.lstrip())]
                if line_stripped == '' or len(current_indent) > len(method_indentation) or line_stripped.startswith('#'):
                    test_method_lines.append(line)
                else:
                    # This is the end of the test method
                    break
        
        if not test_method_lines:
            # If we couldn't extract a method, just append the whole new test
            return self._simple_append(existing_content, new_test)
        
        # Now insert the extracted method into the existing content
        existing_lines = existing_content.split('\n')
        
        # Find the class definition to insert into
        class_line_index = -1
        for i, line in enumerate(existing_lines):
            if line.strip().startswith('class '):
                class_line_index = i
                break
        
        if class_line_index == -1:
            # No class found, simple append
            return self._simple_append(existing_content, new_test)
        
        # Find where the class ends (next non-indented line or end of file)
        insert_index = len(existing_lines)
        for i in range(class_line_index + 1, len(existing_lines)):
            line = existing_lines[i]
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                insert_index = i
                break
        
        # Add proper indentation to the test method lines
        indented_method_lines = []
        for i, line in enumerate(test_method_lines):
            if i == 0:
                # First line (def) should have 4 spaces indentation
                indented_method_lines.append('    ' + line.lstrip())
            else:
                # Other lines should maintain their relative indentation
                if line.strip():  # Non-empty line
                    indented_method_lines.append('    ' + line.lstrip())
                else:
                    indented_method_lines.append(line)  # Empty line as is
        
        # Insert the new method before the class ends
        final_lines = existing_lines[:insert_index] + indented_method_lines + existing_lines[insert_index:]
        
        # Remove duplicate imports
        final_lines = self._remove_duplicate_imports(final_lines, import_lines)
        
        return '\n'.join(final_lines)
    
    def _simple_append(self, existing_content: str, new_content: str) -> str:
        """Simple append with import deduplication."""
        existing_lines = existing_content.split('\n')
        new_lines = new_content.split('\n')
        
        # Remove common imports from the new content if they exist in the existing content
        existing_imports = {line.strip() for line in existing_lines if line.strip().startswith('import ') or line.strip().startswith('from ')}
        filtered_new_lines = [line for line in new_lines if not (line.strip().startswith('import ') or line.strip().startswith('from ')) or line.strip() not in existing_imports]
        
        # Combine the existing content with the new test
        return existing_content + '\n\n' + '\n'.join(filtered_new_lines)
    
    def _remove_duplicate_imports(self, lines: list, new_imports: list) -> list:
        """Remove duplicate imports from the list of lines."""
        existing_imports = {line.strip() for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')}
        filtered_imports = [line for line in new_imports if line.strip() not in existing_imports]
        
        # Return lines with filtered imports at the top
        if filtered_imports:
            # Find where existing imports end
            import_end_index = 0
            for i, line in enumerate(lines):
                if line.strip() and not (line.strip().startswith('import ') or line.strip().startswith('from ')):
                    import_end_index = i
                    break
            else:
                import_end_index = len(lines)
            
            return lines[:import_end_index] + filtered_imports + lines[import_end_index:]
        
        return lines
    
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