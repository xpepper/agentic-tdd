"""
LLM interaction module for agentic-tdd.
This module provides utilities for interacting with various LLM providers.
"""
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
import os


class LLMProvider:
    """Provider for LLM interactions."""
    
    def __init__(self, model: str = "gpt-4", provider: str = "openai", api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model = model
        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.base_url = base_url
        
        # Initialize the LLM based on provider
        if provider.lower() == "openai":
            self.llm = ChatOpenAI(
                model=model,
                api_key=self.api_key,
                temperature=0.7
            )
        else:
            # For other providers that are OpenAI-compatible
            # Use provided base_url if available, otherwise construct from provider name
            if base_url:
                api_base = base_url
            else:
                api_base = f"https://{provider}.openai.com/v1"
            
            self.llm = ChatOpenAI(
                model=model,
                openai_api_key=self.api_key,
                openai_api_base=api_base,
                temperature=0.7
            )
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using the LLM."""
        try:
            response = self.llm.invoke(prompt, **kwargs)
            return response.content
        except Exception as e:
            raise Exception(f"Error generating text with {self.provider}: {str(e)}")
    
    def generate_code(self, prompt: str, language: str = "python") -> str:
        """Generate code using the LLM with code-specific formatting."""
        code_prompt = f"{prompt}\n\nPlease provide the code in a markdown code block."
        
        try:
            response = self.llm.invoke(code_prompt)
            content = response.content
            
            # Extract code from markdown code blocks if present
            if "```" in content:
                # Find the first code block
                start = content.find("```")
                if start != -1:
                    # Check if it's a language-specific code block
                    lang_end = content.find("\n", start)
                    if lang_end != -1:
                        start = lang_end + 1
                    else:
                        start += 3
                    
                    end = content.find("```", start)
                    if end != -1:
                        content = content[start:end].strip()
            
            return content
        except Exception as e:
            raise Exception(f"Error generating code with {self.provider}: {str(e)}")


def create_tester_prompt(kata_description: str, existing_code: str = "", existing_tests: str = "") -> str:
    """Create a prompt for the tester agent to generate a failing test."""
    prompt = f"""
You are a Test-Driven Development expert. Your task is to write a single, focused unit test 
that captures the next required behavior for the kata described below.

Kata Description:
{kata_description}

Instructions:
1. Analyze the kata description to identify the next behavior that should be implemented
2. Write a single, clear unit test that captures this behavior
3. The test should be specific and focused on one aspect of the functionality
4. The test should fail initially (this is the "red" phase of TDD)
5. Do not implement the functionality, only write the test
6. Return only the test code in a valid format for the target language

Existing Code:
{existing_code if existing_code else "No existing code"}

Existing Tests:
{existing_tests if existing_tests else "No existing tests"}

Please provide the test code:
"""
    return prompt


def create_implementer_prompt(kata_description: str, failing_test: str, existing_code: str = "") -> str:
    """Create a prompt for the implementer agent to make a test pass."""
    prompt = f"""
You are a software development expert following Test-Driven Development principles. 
Your task is to implement the minimal code necessary to make the failing test pass.

Kata Description:
{kata_description}

Failing Test:
{failing_test}

Existing Code:
{existing_code if existing_code else "No existing code"}

Instructions:
1. Analyze the failing test to understand what functionality is missing
2. Implement only the minimal code necessary to make this test pass
3. Do not implement additional features beyond what the test requires
4. Keep your implementation simple and focused
5. Ensure all existing functionality continues to work
6. Return only the implementation code

Please provide the implementation code:
"""
    return prompt


def create_refactorer_prompt(kata_description: str, code_to_refactor: str, existing_tests: str) -> str:
    """Create a prompt for the refactorer agent to improve code quality."""
    prompt = f"""
You are a software development expert focused on code quality and maintainability.
Your task is to refactor the provided code to improve its structure, readability, 
and maintainability while ensuring all tests continue to pass.

Kata Description:
{kata_description}

Code to Refactor:
{code_to_refactor}

Existing Tests (for reference):
{existing_tests}

Refactoring Guidelines:
1. Focus on improving code quality without changing behavior
2. Look for opportunities to improve naming, structure, and organization
3. Eliminate duplication and improve clarity
4. Ensure all existing tests continue to pass
5. Make only safe, incremental improvements
6. Do not add new functionality
7. Return only the refactored code

Please provide the refactored code:
"""
    return prompt


def create_commit_message_prompt(agent_type: str, kata_description: str, agent_result: dict, cycle_count: int) -> str:
    """Create a prompt for generating a commit message."""
    # Extract relevant information based on agent type
    if agent_type == "test":
        content_info = f"Test file: {agent_result.get('test_file', 'N/A')}\nTest content preview: {agent_result.get('test_content', '')[:200]}..."
    elif agent_type == "feat":
        content_info = f"Implementation files: {agent_result.get('implementation_files', [])}\nTests pass: {agent_result.get('tests_pass', False)}"
    elif agent_type == "refactor":
        content_info = f"Refactored files: {agent_result.get('refactored_files', [])}\nTests still pass: {agent_result.get('tests_pass', False)}"
    else:
        content_info = "Agent result details not available"
    
    prompt = f"""
You are an expert in writing clear, descriptive git commit messages following conventional commit format.
Your task is to generate a concise but informative commit message based on the work that was done.

Agent Type: {agent_type}
TDD Cycle: {cycle_count}
Kata Description:
{kata_description}

Work Details:
{content_info}

Guidelines for commit messages:
1. Use conventional commit format: {agent_type}: <description>
2. Be concise but descriptive (50-70 characters for the subject line)
3. Focus on what was accomplished, not how it was done
4. Use present tense ("add", "fix", "refactor" not "added", "fixed", "refactored")
5. Be specific about what functionality was affected

Examples:
- test: add failing test for rover movement validation
- feat: implement rover forward movement with boundary checks
- refactor: extract rover heading logic into separate functions

Generate an appropriate commit message:
"""
    return prompt