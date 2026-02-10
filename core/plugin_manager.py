import os
import sys
import importlib.util
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

class PluginManager:
    def __init__(self, plugins_dir: str = "skills/plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.registered_skills: Dict[str, Dict[str, Any]] = {}
        self._load_all_plugins()
    
    def discover_plugins(self) -> List[str]:
        plugins = []
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir() and (plugin_dir / "manifest.yaml").exists():
                plugins.append(plugin_dir.name)
        return plugins
    
    def _load_all_plugins(self):
        for plugin_name in self.discover_plugins():
            try:
                self.load_plugin(plugin_name)
            except Exception as e:
                print(f"Error loading plugin {plugin_name}: {e}")
    
    def load_plugin(self, plugin_name: str) -> Dict[str, Any]:
        plugin_path = self.plugins_dir / plugin_name
        manifest_path = plugin_path / "manifest.yaml"
        
        try:
            if not manifest_path.exists():
                raise FileNotFoundError(f"Manifest file not found for plugin {plugin_name}")
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
            
            skill_path = plugin_path / "skill.py"
            if not skill_path.exists():
                raise FileNotFoundError(f"Skill implementation not found for plugin {plugin_name}")
            
            spec = importlib.util.spec_from_file_location(f"skill_{plugin_name}", skill_path)
            skill_module = importlib.util.module_from_spec(spec)
            sys.modules[f"skill_{plugin_name}"] = skill_module
            spec.loader.exec_module(skill_module)
            
            plugin_info = {
                "name": plugin_name,
                "manifest": manifest,
                "module": skill_module,
                "path": str(plugin_path)
            }
            
            self.registered_skills[plugin_name] = plugin_info
            return plugin_info
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            raise
    
    def get_plugin(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        return self.registered_skills.get(plugin_name)
    
    def execute_plugin(self, plugin_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        plugin_info = self.get_plugin(plugin_name)
        if not plugin_info:
            raise ValueError(f"Plugin {plugin_name} not found")
        
        try:
            if hasattr(plugin_info["module"], "execute"):
                result = plugin_info["module"].execute(parameters)
                return result
            else:
                raise AttributeError(f"Plugin {plugin_name} has no execute function")
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        plugins = []
        for plugin_name, plugin_info in self.registered_skills.items():
            plugins.append({
                "name": plugin_name,
                "description": plugin_info["manifest"].get("description", ""),
                "version": plugin_info["manifest"].get("version", "1.0.0"),
                "category": plugin_info["manifest"].get("category", "general")
            })
        return plugins
    
    def reload_plugins(self):
        self.registered_skills.clear()
        self._load_all_plugins()
        return f"Reloaded {len(self.registered_skills)} plugins"
