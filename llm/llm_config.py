import os
from typing import Dict, Any

# Try to import dotenv, if not installed, don't use it
try:
    from dotenv import load_dotenv
    dotenv_available = True
except ImportError:
    dotenv_available = False

class LLMConfig:
    """LLM configuration class"""
    def __init__(self):
        # Load .env file
        self._load_env()
        
        # Default configuration
        self.default_config = {
            "model": "qwen-turbo",
            "api_key": "",
            "temperature": 0.7,
            "base_url": ""
        }
        
        # Load configuration from environment variables
        self.config = self._get_config_from_env()
    
    def _load_env(self):
        """Load .env file"""
        if dotenv_available:
            # Load .env file
            env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
            if os.path.exists(env_file):
                load_dotenv(env_file)
    
    def _get_config_from_env(self) -> Dict[str, Any]:
        """Get configuration from environment variables"""
        config = self.default_config.copy()
        
        # Load API key
        if "SKILL_AGENT_API_KEY" in os.environ:
            config["api_key"] = os.environ["SKILL_AGENT_API_KEY"]
        
        # Load model
        if "SKILL_AGENT_MODEL" in os.environ:
            config["model"] = os.environ["SKILL_AGENT_MODEL"]
        
        # Load base_url
        if "SKILL_AGENT_BASE_URL" in os.environ:
            config["base_url"] = os.environ["SKILL_AGENT_BASE_URL"]
        
        # Load temperature
        if "SKILL_AGENT_TEMPERATURE" in os.environ:
            try:
                config["temperature"] = float(os.environ["SKILL_AGENT_TEMPERATURE"])
            except ValueError:
                pass
        
        return config
    
    
    
    @property
    def model(self) -> str:
        return self.config["model"]
    
    @property
    def api_key(self) -> str:
        return self.config["api_key"]
    
    @property
    def temperature(self) -> float:
        return self.config["temperature"]
    
    @property
    def base_url(self) -> str:
        return self.config["base_url"]
    
    def get_config(self) -> Dict[str, Any]:
        """Get complete configuration"""
        return self.config

# Create global configuration instance
llm_config = LLMConfig()
