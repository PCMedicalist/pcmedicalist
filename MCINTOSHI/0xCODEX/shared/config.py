"""
Shared configuration for 0xCODEX bot fleet.
Centralized configuration management with environment variable overrides.
"""

import os
from typing import Dict, Any

# Default configuration values
DEFAULT_CONFIG = {
    "RESPONSE_ENGINE": {
        "MODE": "hybrid",  # template_first, llm_only, hybrid
        "LLM_PROVIDER": "openai",
        "LLM_MODEL": "gpt-4",
        "LLM_TEMPERATURE": 0.7,
        "TEMPLATE_FALLBACK": True,
        "MAX_FALLBACK_ATTEMPTS": 3
    },
    "LLM_ENDPOINTS": {
        "OLLAMA_API_URL": "http://host.docker.internal:11435/api",
        "OLLAMA_MODEL_NAME": "gemma3:4b",
        "OLLAMA_API_KEY": "",
        "OPENAI_API_KEY": "",
    },
    "INTER_AGENT_COMM": {
        "ENABLED": True,
        "CHATTER_FREQUENCY": "frequent",  # rare, moderate, frequent
        "AUTO_APPROVAL_GATE": False,  # Soft gates only in phase 1
        "MESSAGE_TTL": 3600,  # 1 hour
        "MAX_CONVERSATION_TURNS": 5,
        "COOLDOWN_PERIOD": 30  # seconds
    },
    "PERSONA_GUARDRAILS": {
        "ENABLED": True,
        "FORBIDDEN_CLAIMS_CHECK": True,
        "AUTHORITY_LEAKAGE_CHECK": True,
        "ROLE_CONSISTENCY_CHECK": True,
        "WARNING_ACTION": "log_warn",  # log_warn, log_error, annotate
    },
    "OBSERVABILITY": {
        "ENABLED": True,
        "TRACE_LEVEL": "info",  # debug, info, warn, error
        "METRICS_COLLECTION": True,
        "LOG_FORMAT": "json"
    }
}

class ConfigManager:
    """Manages configuration for the bot fleet"""
    
    def __init__(self, base_config: Dict[str, Any] = DEFAULT_CONFIG):
        self.config = base_config
        self._load_environment_overrides()
    
    def _load_environment_overrides(self):
        """Load configuration overrides from environment variables"""
        # Response engine settings
        self._set_config_from_env("RESPONSE_ENGINE.MODE", "PERSONA_RESPONSE_MODE")
        self._set_config_from_env("RESPONSE_ENGINE.LLM_PROVIDER", "PERSONA_LLM_PROVIDER")
        self._set_config_from_env("RESPONSE_ENGINE.LLM_MODEL", "PERSONA_LLM_MODEL")
        self._set_config_from_env("RESPONSE_ENGINE.LLM_TEMPERATURE", "PERSONA_LLM_TEMP", float)
        self._set_config_from_env("RESPONSE_ENGINE.TEMPLATE_FALLBACK", "PERSONA_TEMPLATE_FALLBACK", bool)

        # LLM endpoint settings
        self._set_config_from_env("LLM_ENDPOINTS.OLLAMA_API_URL", "OLLAMA_API_URL")
        self._set_config_from_env("LLM_ENDPOINTS.OLLAMA_MODEL_NAME", "OLLAMA_MODEL_NAME")
        self._set_config_from_env("LLM_ENDPOINTS.OLLAMA_MODEL_NAME", "OLLAMA_LOCAL_MODEL_NAME")
        self._set_config_from_env("LLM_ENDPOINTS.OLLAMA_API_KEY", "OLLAMA_API_KEY")
        self._set_config_from_env("LLM_ENDPOINTS.OPENAI_API_KEY", "OPENAI_API_KEY")
        
        # Inter-agent communication settings
        self._set_config_from_env("INTER_AGENT_COMM.ENABLED", "INTER_AGENT_ENABLED", bool)
        self._set_config_from_env("INTER_AGENT_COMM.CHATTER_FREQUENCY", "CHATTER_FREQUENCY")
        self._set_config_from_env("INTER_AGENT_COMM.AUTO_APPROVAL_GATE", "AUTO_APPROVAL_GATE", bool)
        
        # Persona guardrails settings
        self._set_config_from_env("PERSONA_GUARDRAILS.ENABLED", "GUARDRAILS_ENABLED", bool)
        self._set_config_from_env("PERSONA_GUARDRAILS.WARNING_ACTION", "GUARDRAILS_WARNING_ACTION")
        
        # Observability settings
        self._set_config_from_env("OBSERVABILITY.ENABLED", "OBSERVABILITY_ENABLED", bool)
        self._set_config_from_env("OBSERVABILITY.TRACE_LEVEL", "TRACE_LEVEL")
    
    def _set_config_from_env(self, config_path: str, env_var: str, cast_type=None):
        """Set a configuration value from an environment variable"""
        value = os.environ.get(env_var)
        if value is not None:
            if cast_type:
                if cast_type == bool:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                else:
                    value = cast_type(value)
            
            # Set nested config value
            keys = config_path.split('.')
            config_section = self.config
            for key in keys[:-1]:
                config_section = config_section[key]
            config_section[keys[-1]] = value
    
    def get(self, path: str, default=None):
        """Get a configuration value using dot notation path"""
        keys = path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            return default

# Global config instance
config = ConfigManager()

# Convenience functions for common config access
def get_response_mode():
    return config.get("RESPONSE_ENGINE.MODE", "hybrid")

def get_chatter_frequency():
    return config.get("INTER_AGENT_COMM.CHATTER_FREQUENCY", "frequent")

def are_guardrails_enabled():
    return config.get("PERSONA_GUARDRAILS.ENABLED", True)

def is_inter_agent_comm_enabled():
    return config.get("INTER_AGENT_COMM.ENABLED", True)


def get_llm_provider() -> str:
    return config.get("RESPONSE_ENGINE.LLM_PROVIDER", "openai")


def get_llm_model() -> str:
    return config.get("RESPONSE_ENGINE.LLM_MODEL", "gpt-4")


def get_llm_temperature() -> float:
    return float(config.get("RESPONSE_ENGINE.LLM_TEMPERATURE", 0.7))


def get_ollama_api_url() -> str:
    return config.get("LLM_ENDPOINTS.OLLAMA_API_URL", "http://host.docker.internal:11435/api")


def get_ollama_model_name() -> str:
    return config.get("LLM_ENDPOINTS.OLLAMA_MODEL_NAME", "gemma3:4b")


def get_ollama_api_key() -> str:
    return config.get("LLM_ENDPOINTS.OLLAMA_API_KEY", "")


def get_openai_api_key() -> str:
    return config.get("LLM_ENDPOINTS.OPENAI_API_KEY", "")