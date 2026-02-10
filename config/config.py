import yaml
import os
from typing import Dict, Any, Optional

class Config:
    def __init__(self, config_data=None):
        # Default configuration
        self.default_config = {
            "plugin": {
                "name": "skill_agent",
                "version": "1.0.0",
                "description": "Agent self-evolution plugin"
            },
            "skills": {
                "plugins_dir": "skills/plugins",
                "auto_load": True,
                "max_skills": 100
            },
            "templates": {
                "dir": "templates",
                "default_template": "base_skill"
            },
            "security": {
                "enable_code_validation": True,
                "allow_external_dependencies": False
            }
        }
        
        # Load configuration
        if config_data:
            self.config = self._merge_configs(self.default_config, config_data)
        else:
            self.config = self.default_config
        
        # Load API key from environment variables
        self._load_from_env()
    
    def _merge_configs(self, default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge configurations"""
        merged = default.copy()
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # LLM-related configuration has been moved to llm/llm_config.py
        pass
    
    @property
    def plugin(self):
        return ConfigDict(self.config.get("plugin", {}))
    
    
    
    @property
    def skills(self):
        return ConfigDict(self.config.get("skills", {}))
    
    @property
    def templates(self):
        return ConfigDict(self.config.get("templates", {}))
    
    @property
    def security(self):
        return ConfigDict(self.config.get("security", {}))

class ConfigDict:
    """Configuration dictionary with attribute access support"""
    def __init__(self, data):
        self.__dict__.update(data)
    
    def __getattr__(self, name):
        return None
    
    def get(self, key, default=None):
        """Get configuration value"""
        return getattr(self, key, default)

# Add file loading and saving methods to Config class
def load_from_file(self, config_file: str) -> bool:
    """Load configuration from file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        if config_data:
            self.config = self._merge_configs(self.default_config, config_data)
            self._load_from_env()
        return True
    except Exception as e:
        print(f"Failed to load configuration file: {e}")
        return False

def save_to_file(self, config_file: str) -> bool:
    """Save configuration to file"""
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, sort_keys=False)
        return True
    except Exception as e:
        print(f"Failed to save configuration file: {e}")
        return False

# Add methods to Config class
Config.load_from_file = load_from_file
Config.save_to_file = save_to_file
