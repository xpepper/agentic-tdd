"""Configuration module for agentic-tdd."""

import os
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """Configuration for an individual agent."""

    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    max_retries: int = 3


@dataclass
class Config:
    """Main configuration for agentic-tdd."""

    # LLM configuration
    default_model: str = "gpt-3.5-turbo"
    api_keys: Dict[str, str] = field(default_factory=dict)

    # Agent configurations
    tester_config: AgentConfig = field(default_factory=AgentConfig)
    implementer_config: AgentConfig = field(default_factory=AgentConfig)
    refactorer_config: AgentConfig = field(default_factory=AgentConfig)
    supervisor_config: AgentConfig = field(default_factory=AgentConfig)

    # TDD process configuration
    max_tdd_cycles: int = 20
    enable_git_staging: bool = True
    verbose_output: bool = True

    def __post_init__(self):
        """Initialize configuration with environment variables."""
        # Load API keys from environment variables
        self._load_api_keys_from_env()

    def _load_api_keys_from_env(self) -> None:
        """Load API keys from environment variables."""
        # Common API key environment variables
        api_key_vars = [
            "OPENAI_API_KEY",
            "PERPLEXITY_API_KEY",
            "DEEPSEEK_API_KEY",
            "ANTHROPIC_API_KEY",
            "GROQ_API_KEY",
        ]

        for var_name in api_key_vars:
            api_key = os.getenv(var_name)
            if api_key:
                # Use the provider name as the key (e.g., "openai" for "OPENAI_API_KEY")
                provider_name = var_name.replace("_API_KEY", "").lower()
                self.api_keys[provider_name] = api_key

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        return self.api_keys.get(provider.lower())

    def set_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for a specific provider."""
        self.api_keys[provider.lower()] = api_key

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        config = cls()

        # Override default model if specified
        default_model = os.getenv("DEFAULT_MODEL")
        if default_model:
            config.default_model = default_model

        # Override max TDD cycles if specified
        max_cycles = os.getenv("MAX_TDD_CYCLES")
        if max_cycles:
            try:
                config.max_tdd_cycles = int(max_cycles)
            except ValueError:
                pass  # Keep default value

        # Override git staging setting
        enable_git_staging = os.getenv("ENABLE_GIT_STAGING")
        if enable_git_staging is not None:
            config.enable_git_staging = enable_git_staging.lower() in (
                "true",
                "1",
                "yes",
            )

        # Override verbose output setting
        verbose_output = os.getenv("VERBOSE_OUTPUT")
        if verbose_output is not None:
            config.verbose_output = verbose_output.lower() in ("true", "1", "yes")

        return config


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = Config.from_env()
    return _global_config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _global_config
    _global_config = config
