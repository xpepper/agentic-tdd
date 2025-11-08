"""
Core module for the Multi-Agent TDD system.
This module defines the main classes and interfaces for the agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
from pathlib import Path
from .logger import get_agent_logger


class AgentException(Exception):
    """Custom exception for agent-related errors."""
    pass


class Agent(ABC):
    """Abstract base class for all agents in the TDD system."""
    
    def __init__(self, name: str, work_dir: str, kata_description: str, config=None):
        self.name = name
        self.work_dir = Path(work_dir)
        self.kata_description = kata_description
        self.config = config
        self.logger = get_agent_logger(name, work_dir)
        
        try:
            self.kata_content = self._load_kata_content()
            self.logger.info(f"Successfully loaded kata description from {kata_description}")
        except Exception as e:
            self.logger.error(f"Failed to load kata description: {str(e)}")
            raise AgentException(f"Could not load kata description: {str(e)}")
    
    def _load_kata_content(self) -> str:
        """Load the kata description content from file."""
        try:
            with open(self.kata_description, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise AgentException(f"Kata description file not found: {self.kata_description}")
        except Exception as e:
            raise AgentException(f"Error reading kata description file: {str(e)}")
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the agent's specific role in the TDD cycle."""
        pass


class AgentConfig:
    """Configuration for the multi-agent system."""
    
    def __init__(self, 
                 model: str = "gpt-4",
                 provider: str = "openai", 
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 max_cycles: int = 10):
        self.model = model
        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.base_url = base_url
        self.max_cycles = max_cycles