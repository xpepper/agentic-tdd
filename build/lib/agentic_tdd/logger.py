"""
Logging module for agentic-tdd.
This module provides centralized logging functionality for all agents.
"""
import logging
import sys
from pathlib import Path
from typing import Optional


class AgentLogger:
    """Centralized logger for agentic-tdd agents."""
    
    def __init__(self, name: str, log_file: Optional[str] = None, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Prevent adding multiple handlers if logger already exists
        if not self.logger.handlers:
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # Create file handler if specified
            if log_file:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)


def get_agent_logger(agent_name: str, work_dir: Optional[str] = None) -> AgentLogger:
    """Get a logger for a specific agent."""
    if work_dir:
        log_file = Path(work_dir) / f"{agent_name.lower()}_log.txt"
        return AgentLogger(agent_name, str(log_file))
    else:
        return AgentLogger(agent_name)