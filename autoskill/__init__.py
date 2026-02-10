import os
from typing import Dict, Any, Optional, List
from core.plugin_manager import PluginManager
from core.skill_registry import SkillRegistry
from core.skill_executor import SkillExecutor
from core.skill_generator import SkillGenerator
from core.skill_persistence import SkillPersistence
from core.skill_fingerprint import SkillFingerprintManager
from llm.skill_creator import LLMSkillCreator
from llm.reflection_engine import ReflectionEngine
from llm.llm_config import llm_config
from config.config import Config
from templates.template_registry import TemplateRegistry

# Plugin version information
__version__ = "1.0.0"
__min_python_version__ = "3.11"
__supported_langchain_version__ = ">=0.1.0"

# Error code definitions
ERROR_CODES = {
    "SKILL_NOT_FOUND": (404, "Skill not found"),
    "SKILL_EXECUTION_FAILED": (500, "Skill execution failed"),
    "SKILL_CREATION_FAILED": (500, "Skill creation failed"),
    "INVALID_PARAMETERS": (400, "Invalid parameters"),
    "NETWORK_ERROR": (503, "Network error"),
    "INTERNAL_ERROR": (500, "Internal error")
}

class AutoSkillError(Exception):
    """
    AutoSkill exception base class
    """
    def __init__(self, error_code: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize exception
        
        Args:
            error_code: Error code
            message: Error message
            details: Error details
        """
        self.error_code = error_code
        self.status_code, default_message = ERROR_CODES.get(error_code, (500, "Unknown error"))
        self.message = message or default_message
        self.details = details or {}
        super().__init__(f"[{error_code}] {self.message}")

class AutoSkill:
    def __init__(self, config=None, isolation_level="none"):
        """
        Initialize AutoSkill
        
        Args:
            config: Config dictionary containing paths for skills and templates
            isolation_level: Environment isolation level, options: none, venv, custom
        """
        # Get absolute path to plugin directory
        plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Create relative paths
        skills_dir = os.path.join(plugin_dir, "skills")
        templates_dir = os.path.join(plugin_dir, "templates")
        
        # Override paths in config
        if config is None:
            config = {}
        if "skills" not in config:
            config["skills"] = {}
        config["skills"]["plugins_dir"] = skills_dir
        if "templates" not in config:
            config["templates"] = {}
        config["templates"]["dir"] = templates_dir
        
        self.config = Config(config)
        self.plugin_manager = PluginManager(self.config.skills.plugins_dir)
        self.skill_registry = SkillRegistry()
        self.skill_executor = SkillExecutor(self.plugin_manager, isolation_level)
        self.skill_generator = SkillGenerator(self.config.skills.plugins_dir)
        self.skill_persistence = SkillPersistence(self.config.skills.plugins_dir)
        self.template_registry = TemplateRegistry(self.config.templates.dir)
        self.skill_fingerprint_manager = SkillFingerprintManager()
        self._initialize_registry()
        self._initialize_fingerprints()
    
    def set_isolation_level(self, isolation_level):
        """
        Set environment isolation level
        
        Args:
            isolation_level: Isolation level, options: none, venv, custom
        """
        self.skill_executor.set_isolation_level(isolation_level)
    
    def get_isolation_level(self):
        """
        Get current environment isolation level
        
        Returns:
            str: Current isolation level
        """
        return self.skill_executor.isolation_level
    
    def register_isolation_strategy(self, name, strategy):
        """
        Register custom isolation strategy
        
        Args:
            name: Strategy name
            strategy: Strategy object, should implement execute method
        """
        self.skill_executor.register_isolation_strategy(name, strategy)
    
    def _initialize_registry(self):
        """
        Initialize skill registry
        
        Load all registered skills from plugin manager and register them to skill registry
        """
        for plugin_name, plugin_info in self.plugin_manager.registered_skills.items():
            manifest = plugin_info.get("manifest", {})
            skill_metadata = {
                "name": plugin_name,
                "description": manifest.get("description", ""),
                "version": manifest.get("version", "1.0.0"),
                "category": manifest.get("category", "general"),
                "parameters": manifest.get("parameters", {}),
                "dependencies": manifest.get("environment", {}).get("dependencies", [])
            }
            self.skill_registry.register_skill(plugin_name, skill_metadata)
    
    def _initialize_fingerprints(self):
        """
        Initialize fingerprints for existing skills
        """
        for plugin_name, plugin_info in self.plugin_manager.registered_skills.items():
            manifest = plugin_info.get("manifest", {})
            description = manifest.get("description", "")
            
            # Try to read skill code
            skill_path = os.path.join(self.plugin_manager.plugins_dir, plugin_name, "skill.py")
            code = None
            if os.path.exists(skill_path):
                try:
                    with open(skill_path, "r", encoding="utf-8") as f:
                        code = f.read()
                except Exception as e:
                    print(f"Failed to read skill code: {e}")
            
            # Register skill fingerprint
            if description:
                self.skill_fingerprint_manager.register_skill(plugin_name, description, code)
    
    def execute_skill(self, skill_name: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute skill
        
        Args:
            skill_name: Skill name
            parameters: Execution parameters
            
        Returns:
            Dict[str, Any]: Execution result
            
        Raises:
            AutoSkillError: Error executing skill
        """
        if parameters is None:
            parameters = {}
        
        try:
            result = self.skill_executor.execute(skill_name, parameters)
            
            # Handle non-dict return values
            if not isinstance(result, dict):
                # If return value is string, try to parse as JSON
                if isinstance(result, str):
                    try:
                        import json
                        result = json.loads(result)
                    except json.JSONDecodeError:
                        # If parsing fails, wrap as success result
                        return {"success": True, "result": result}
                else:
                    # Directly wrap other types as success result
                    return {"success": True, "result": result}
            
            # Handle dict return values
            # Check if success field exists and is False
            if "success" in result and not result["success"]:
                raise AutoSkillError(
                    "SKILL_EXECUTION_FAILED",
                    result.get("error", "Skill execution failed"),
                    {"skill_name": skill_name, "parameters": parameters}
                )
            return result
        except Exception as e:
            if isinstance(e, AutoSkillError):
                raise
            raise AutoSkillError(
                "SKILL_EXECUTION_FAILED",
                str(e),
                {"skill_name": skill_name, "parameters": parameters}
            )
    
    def create_skill(self, skill_name: str, task_description: str, template: Optional[str] = None) -> str:
        """
        Create skill
        
        Args:
            skill_name: Skill name
            task_description: Task description
            template: Template name
            
        Returns:
            str: Skill path
            
        Raises:
            AutoSkillError: Error creating skill
        """
        try:
            # Check for duplicate skills
            is_duplicate, duplicate_skill, similarity = self.skill_fingerprint_manager.check_duplicate(task_description, threshold=0.8)
            if is_duplicate:
                # Found duplicate skill, return information about loaded existing skill
                skill_info = self.get_skill_info(duplicate_skill)
                if skill_info:
                    return f"Found duplicate skill '{duplicate_skill}' (similarity: {similarity:.2f}), automatically loaded existing skill.\nSkill info: {skill_info}"
                else:
                    return f"Found duplicate skill '{duplicate_skill}' (similarity: {similarity:.2f}), but failed to load, please check skill status."
            
            if template:
                template_content = self.template_registry.get_template(template)
                if template_content:
                    task_description = f"{template_content}\n\n{task_description}"
            
            # Create skill using plugin's internal path
            skill_creator = LLMSkillCreator(llm_config.api_key, self.plugin_manager.plugins_dir)
            skill_path = skill_creator.create_skill(skill_name, task_description)
            
            # Register fingerprint for new skill
            # Read skill code
            skill_module_path = os.path.join(skill_path, "skill.py")
            code = None
            if os.path.exists(skill_module_path):
                try:
                    with open(skill_module_path, "r", encoding="utf-8") as f:
                        code = f.read()
                except Exception as e:
                    print(f"Failed to read skill code: {e}")
            
            # Register skill fingerprint using original task description to ensure language consistency
            self.skill_fingerprint_manager.register_skill(skill_name, task_description, code)
            
            # Reload plugins to ensure new skill is included in skill list
            self.plugin_manager.reload_plugins()
            self.skill_registry.clear()
            self._initialize_registry()
            
            return skill_path
        except Exception as e:
            if isinstance(e, AutoSkillError):
                raise
            raise AutoSkillError(
                "SKILL_CREATION_FAILED",
                str(e),
                {"skill_name": skill_name, "task_description": task_description}
            )
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """
        List all available skills
        
        Returns:
            List[Dict[str, Any]]: Skill list
        """
        return self.skill_executor.list_available_skills()
    
    def get_skill_info(self, skill_name: str) -> Dict[str, Any]:
        """
        Get skill information
        
        Args:
            skill_name: Skill name
            
        Returns:
            Dict[str, Any]: Skill information
            
        Raises:
            AutoSkillError: Error getting skill information
        """
        try:
            result = self.skill_executor.get_skill_info(skill_name)
            if not result.get("success", True):
                raise AutoSkillError(
                    "SKILL_NOT_FOUND",
                    result.get("error", "Skill not found"),
                    {"skill_name": skill_name}
                )
            # If result contains "skill" field, return its value
            if "skill" in result:
                return result["skill"]
            return result
        except Exception as e:
            if isinstance(e, AutoSkillError):
                raise
            raise AutoSkillError(
                "SKILL_NOT_FOUND",
                str(e),
                {"skill_name": skill_name}
            )
    
    def update_skill(self, skill_name: str, improvements: str) -> Dict[str, Any]:
        """
        Update skill
        
        Args:
            skill_name: Skill name
            improvements: Improvement description
            
        Returns:
            Dict[str, Any]: Update result
        """
        # Implement skill update logic
        return {"success": False, "error": "Not implemented"}
    
    def delete_skill(self, skill_name: str) -> Dict[str, Any]:
        """
        Delete skill
        
        Args:
            skill_name: Skill name
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        try:
            # 1. Check if skill exists
            plugin_info = self.plugin_manager.get_plugin(skill_name)
            if not plugin_info:
                return {"success": False, "error": f"Skill '{skill_name}' not found"}
            
            # 2. Get skill path
            skill_path = plugin_info.get("path")
            if not skill_path:
                return {"success": False, "error": "Skill path not found"}
            
            # 3. Delete skill directory
            import shutil
            if os.path.exists(skill_path):
                shutil.rmtree(skill_path)
                print(f"Deleted skill directory: {skill_path}")
            
            # 4. Remove skill from fingerprint manager
            self.skill_fingerprint_manager.remove_skill(skill_name)
            print(f"Removed skill fingerprint: {skill_name}")
            
            # 5. Reload plugins and skill registry
            self.reload_skills()
            print(f"Reloaded skills after deletion")
            
            return {"success": True, "message": f"Skill '{skill_name}' deleted successfully"}
        except Exception as e:
            return {"success": False, "error": f"Failed to delete skill: {str(e)}"}
    
    def reload_skills(self) -> str:
        """
        Reload skills
        
        Returns:
            str: Reload result
        """
        self.plugin_manager.reload_plugins()
        self.skill_registry.clear()
        self._initialize_registry()
        return f"Reloaded {len(self.skill_registry.get_all_skills())} skills"
    
    def create_llm_skill_creator(self, api_key: Optional[str] = None) -> LLMSkillCreator:
        """
        Create LLM skill creator
        
        Args:
            api_key: API key
            
        Returns:
            LLMSkillCreator: LLM skill creator instance
        """
        return LLMSkillCreator(api_key or llm_config.api_key, self.plugin_manager.plugins_dir)
    
    @classmethod
    def get_version(cls) -> Dict[str, str]:
        """
        Get plugin version information
        
        Returns:
            Dict[str, str]: Version information
        """
        return {
            "version": __version__,
            "min_python_version": __min_python_version__,
            "supported_langchain_version": __supported_langchain_version__
        }
    
    @classmethod
    def check_compatibility(cls, langchain_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Check compatibility
        
        Args:
            langchain_version: Langchain version
            
        Returns:
            Dict[str, Any]: Compatibility check result
        """
        import sys
        import pkg_resources
        
        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        min_python_major, min_python_minor = map(int, __min_python_version__.split("."))
        python_compatible = (
            sys.version_info.major > min_python_major or
            (sys.version_info.major == min_python_major and sys.version_info.minor >= min_python_minor)
        )
        
        # Check Langchain version
        langchain_compatible = True
        langchain_error = None
        
        if langchain_version:
            # If Langchain version is provided, check directly
            try:
                from packaging.version import parse as parse_version
                current_version = parse_version(langchain_version)
                required_version = parse_version(__supported_langchain_version__.lstrip(">="))
                langchain_compatible = current_version >= required_version
            except Exception as e:
                langchain_error = str(e)
                langchain_compatible = False
        else:
            # Try to get Langchain version from installed packages
            try:
                langchain_version = pkg_resources.get_distribution("langchain").version
                from packaging.version import parse as parse_version
                current_version = parse_version(langchain_version)
                required_version = parse_version(__supported_langchain_version__.lstrip(">="))
                langchain_compatible = current_version >= required_version
            except pkg_resources.DistributionNotFound:
                langchain_error = "Langchain not installed (optional dependency)"
                langchain_compatible = True  # Optional dependency, doesn't affect overall compatibility
            except Exception as e:
                langchain_error = str(e)
                langchain_compatible = False
        
        return {
            "python": {
                "current": python_version,
                "required": __min_python_version__,
                "compatible": python_compatible
            },
            "langchain": {
                "current": langchain_version,
                "required": __supported_langchain_version__,
                "compatible": langchain_compatible,
                "error": langchain_error
            },
            "overall_compatible": python_compatible and langchain_compatible
        }

__all__ = ["AutoSkill", "AutoSkillError", "__version__"]
