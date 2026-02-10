from typing import Dict, List, Any
from core.plugin_manager import PluginManager
from core.isolation_manager import IsolationManager

class SkillExecutor:
    def __init__(self, plugin_manager: PluginManager, isolation_level: str = "none"):
        """
        Initialize skill executor
        
        Args:
            plugin_manager: Plugin manager
            isolation_level: Isolation level, options: none, venv, custom
        """
        self.plugin_manager = plugin_manager
        self.isolation_level = isolation_level
        self.isolation_manager = IsolationManager()
    
    def execute(self, skill_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute skill
        
        Args:
            skill_name: Skill name
            parameters: Execution parameters
            
        Returns:
            Dict[str, Any]: Execution result
        """
        if parameters is None:
            parameters = {}
        
        try:
            if self.isolation_level == "venv":
                return self._execute_in_venv(skill_name, parameters)
            elif self.isolation_level == "custom":
                return self._execute_with_custom_isolation(skill_name, parameters)
            else:
                # Default direct execution
                result = self.plugin_manager.execute_plugin(skill_name, parameters)
                return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_in_venv(self, skill_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute skill in virtual environment
        
        Args:
            skill_name: Skill name
            parameters: Execution parameters
            
        Returns:
            Dict[str, Any]: Execution result
        """
        try:
            # Get skill information
            plugin_info = self.plugin_manager.get_plugin(skill_name)
            if not plugin_info:
                return {
                    "success": False,
                    "error": f"Skill {skill_name} not found"
                }
            
            # Get skill path and dependencies
            skill_path = plugin_info.get("path")
            if not skill_path:
                return {
                    "success": False,
                    "error": f"Skill {skill_name} path not found"
                }
            
            manifest = plugin_info.get("manifest", {})
            dependencies = manifest.get("environment", {}).get("dependencies", [])
            
            # Clean dependency format
            clean_deps = []
            for dep in dependencies:
                if isinstance(dep, str) and dep and dep != "none" and dep != "```":
                    clean_deps.append(dep)
            
            # Create virtual environment
            env_name = f"env_{skill_name}"
            env_path = self.isolation_manager.create_virtualenv(env_name)
            
            # Install dependencies
            self.isolation_manager.install_dependencies(env_name, clean_deps)
            
            # Create temporary execution script
            import os
            import tempfile
            import json
            
            # Create script content, using plain string to avoid format specifier conflicts
            script_content = '''
import sys
import json
import os

# Add skill path to Python path
sys.path.insert(0, "{skill_path}")

# Import skill module
try:
    from main import execute
except ImportError:
    try:
        from skill import execute
    except ImportError:
        print(json.dumps({"success": False, "error": "Failed to import execute function"}))
        sys.exit(1)

try:
    # Parse parameters
    params = json.loads(sys.argv[1])
    # Execute skill
    result = execute(params)
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}))
'''
            
            # Replace skill path
            script_content = script_content.format(skill_path=skill_path)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                temp_script = f.name
            
            try:
                # Execute script in virtual environment
                result = self.isolation_manager.execute_in_venv(env_name, temp_script, parameters)
                return result
            finally:
                # Clean up temporary script
                if os.path.exists(temp_script):
                    os.unlink(temp_script)
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_with_custom_isolation(self, skill_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute skill with custom isolation strategy
        
        Args:
            skill_name: Skill name
            parameters: Execution parameters
            
        Returns:
            Dict[str, Any]: Execution result
        """
        # Here you can implement custom isolation strategy execution as needed
        # For example, call user-registered isolation strategy
        return self.plugin_manager.execute_plugin(skill_name, parameters)
    
    def register_isolation_strategy(self, name: str, strategy: Any):
        """
        Register custom isolation strategy
        
        Args:
            name: Strategy name
            strategy: Strategy object, should implement execute method
        """
        self.isolation_manager.register_isolation_strategy(name, strategy)
    
    def set_isolation_level(self, level: str):
        """
        Set isolation level
        
        Args:
            level: Isolation level, options: none, venv, custom
        """
        self.isolation_level = level
    
    def get_skill_info(self, skill_name: str) -> Dict[str, Any]:
        plugin_info = self.plugin_manager.get_plugin(skill_name)
        if not plugin_info:
            return {
                "success": False,
                "error": f"Skill {skill_name} not found"
            }
        
        manifest = plugin_info.get("manifest", {})
        return {
            "success": True,
            "skill": {
                "name": skill_name,
                "description": manifest.get("description", ""),
                "version": manifest.get("version", "1.0.0"),
                "category": manifest.get("category", "general"),
                "parameters": manifest.get("parameters", {}),
                "dependencies": manifest.get("environment", {}).get("dependencies", [])
            }
        }
    
    def list_available_skills(self) -> List[Dict[str, Any]]:
        return self.plugin_manager.list_plugins()
