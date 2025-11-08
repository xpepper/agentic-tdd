"""Tests for the configuration module."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_config_import():
    """Test that the Config module can be imported."""
    from tdd_agents.config import Config, AgentConfig
    assert Config is not None
    assert AgentConfig is not None


def test_config_initialization():
    """Test that the Config can be initialized."""
    from tdd_agents.config import Config, AgentConfig
    
    config = Config()
    assert config is not None
    assert isinstance(config.tester_config, AgentConfig)
    assert isinstance(config.implementer_config, AgentConfig)
    assert isinstance(config.refactorer_config, AgentConfig)
    assert isinstance(config.supervisor_config, AgentConfig)
    assert config.max_tdd_cycles == 20
    assert config.enable_git_staging
    assert config.verbose_output


def test_config_api_keys():
    """Test API key handling in Config."""
    from tdd_agents.config import Config
    
    config = Config()
    
    # Test setting and getting API keys
    config.set_api_key("openai", "test-openai-key")
    config.set_api_key("perplexity", "test-perplexity-key")
    
    assert config.get_api_key("openai") == "test-openai-key"
    assert config.get_api_key("perplexity") == "test-perplexity-key"
    assert config.get_api_key("unknown") is None


@patch.dict(os.environ, {
    "OPENAI_API_KEY": "env-openai-key",
    "PERPLEXITY_API_KEY": "env-perplexity-key",
    "DEFAULT_MODEL": "gpt-4",
    "MAX_TDD_CYCLES": "10"
})
def test_config_from_env():
    """Test creating configuration from environment variables."""
    from tdd_agents.config import Config
    
    config = Config.from_env()
    
    # Check that API keys were loaded from environment
    assert config.get_api_key("openai") == "env-openai-key"
    assert config.get_api_key("perplexity") == "env-perplexity-key"
    
    # Check that other settings were loaded from environment
    assert config.default_model == "gpt-4"
    assert config.max_tdd_cycles == 10


def test_config_singleton():
    """Test the global configuration singleton."""
    from tdd_agents.config import get_config, set_config, Config
    
    # Get the global config
    config1 = get_config()
    assert config1 is not None
    
    # Get it again - should be the same instance
    config2 = get_config()
    assert config1 is config2
    
    # Create a new config and set it as global
    new_config = Config()
    new_config.max_tdd_cycles = 999
    set_config(new_config)
    
    # Get the global config again - should be the new one
    config3 = get_config()
    assert config3 is new_config
    assert config3.max_tdd_cycles == 999