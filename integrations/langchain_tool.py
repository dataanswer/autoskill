try:
    from langchain_core.tools import Tool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    Tool = None

from typing import Dict, Any, Optional
from autoskill import AutoSkill

class AutoSkillTool(Tool):
    """
    Langchain Tool for AutoSkill
    
    This tool allows Langchain Agent to use AutoSkill to create and execute skills
    """
    
    def __init__(self, skill_agent: Optional[AutoSkill] = None, isolation_level: str = "none"):
        """
        Initialize AutoSkill Tool
        
        Args:
            skill_agent: Optional AutoSkill instance, will create a new instance if not provided
            isolation_level: Environment isolation level, options: none, venv, custom
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain library not installed. Please install the langchain dependency:\n"
                "pip install autoskill-ai[langchain]"
            )
        
        # Create AutoSkill instance
        if skill_agent is None:
            _skill_agent = AutoSkill(isolation_level=isolation_level)
        else:
            _skill_agent = skill_agent
        
        # Call parent class initialization
        super().__init__(
            name="AutoSkill",
            func=self._run,
            description="""Use AutoSkill to execute or create skills
            
            Usage:
            1. Execute existing skill: Provide skill name and parameters
            2. Create new skill: Provide skill name and task description
            
            Parameter format:
            - Execute skill: {"action": "execute", "skill_name": "skill name", "parameters": {"param1": "value1", "param2": "value2"}}
            - Create skill: {"action": "create", "skill_name": "skill name", "task_description": "task description"}
            
            Examples:
            - Execute skill: {"action": "execute", "skill_name": "calculator", "parameters": {"expression": "2 + 2"}}
            - Create skill: {"action": "create", "skill_name": "weather_checker", "task_description": "Create a weather checking skill that takes a city name and returns the current weather for that city"}
            """
        )
        
        # Use __dict__ to bypass Pydantic field checking
        self.__dict__['_skill_agent'] = _skill_agent
    
    @property
    def skill_agent(self):
        """
        Get internal AutoSkill instance
        
        Returns:
            AutoSkill: Internal AutoSkill instance
        """
        return self.__dict__.get('_skill_agent')
    
    def _run(self, input_str: str) -> str:
        """
        Execute AutoSkill operation
        
        Args:
            input_str: JSON format input string containing operation type and parameters
            
        Returns:
            str: String representation of operation result
        """
        import json
        
        try:
            # Check if input string is empty
            if not input_str:
                return "Error: Input string cannot be empty"
                
            # Parse JSON input
            input_data = json.loads(input_str)
            
            # Check if input_data is a dictionary
            if not isinstance(input_data, dict):
                return "Error: Input must be a valid JSON object"
                
            action = input_data.get("action")
            
            if not action:
                return "Error: Must provide operation type (action)"
                
            if action == "execute":
                skill_name = input_data.get("skill_name")
                parameters = input_data.get("parameters", {})
                
                if not skill_name:
                    return "Error: Must provide skill name when executing skill"
                
                if not isinstance(parameters, dict):
                    return "Error: parameters must be a valid JSON object"
                
                # Check if skill_agent is initialized
                skill_agent = self.__dict__.get('_skill_agent')
                if not skill_agent:
                    return "Error: AutoSkill not initialized"
                
                try:
                    result = skill_agent.execute_skill(skill_name, parameters)
                    return json.dumps(result, ensure_ascii=False)
                except Exception as e:
                    return f"Error: Failed to execute skill: {str(e)}"
            
            elif action == "create":
                skill_name = input_data.get("skill_name")
                task_description = input_data.get("task_description")
                
                if not skill_name:
                    return "Error: Must provide skill name when creating skill"
                
                if not task_description:
                    return "Error: Must provide task description when creating skill"
                
                # Check if skill_agent is initialized
                skill_agent = self.__dict__.get('_skill_agent')
                if not skill_agent:
                    return "Error: AutoSkill not initialized"
                
                try:
                    result = skill_agent.create_skill(skill_name, task_description)
                    return f"Success: Skill created successfully, path: {str(result)}"
                except Exception as e:
                    return f"Error: Failed to create skill: {str(e)}"
            
            else:
                return f"Error: Unsupported operation type: {action}, supported operation types: execute, create"
        
        except json.JSONDecodeError as e:
            return f"Error: Invalid input format, must be a valid JSON string: {str(e)}"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error: Operation execution failed: {str(e)}"

    def list_skills(self) -> str:
        """
        List all available skills
        
        Returns:
            str: List of available skills
        """
        skills = self.__dict__.get('_skill_agent').list_skills()
        import json
        return json.dumps(skills, ensure_ascii=False)

    def get_skill_info(self, skill_name: str) -> str:
        """
        Get skill information
        
        Args:
            skill_name: Skill name
            
        Returns:
            str: JSON string of skill information
        """
        info = self.__dict__.get('_skill_agent').get_skill_info(skill_name)
        import json
        return json.dumps(info, ensure_ascii=False)

    def set_isolation_level(self, isolation_level: str) -> str:
        """
        Set environment isolation level
        
        Args:
            isolation_level: Isolation level, options: none, venv, custom
            
        Returns:
            str: Set result
        """
        try:
            self.__dict__.get('_skill_agent').set_isolation_level(isolation_level)
            return f"Success: Environment isolation level set to {isolation_level}"
        except Exception as e:
            return f"Error: Failed to set isolation level: {str(e)}"

    def get_isolation_level(self) -> str:
        """
        Get current environment isolation level
        
        Returns:
            str: Current isolation level
        """
        return self.__dict__.get('_skill_agent').get_isolation_level()


def create_auto_skill_tool(isolation_level: str = "none") -> AutoSkillTool:
    """
    Convenience function to create AutoSkill Tool
    
    Args:
        isolation_level: Environment isolation level, options: none, venv, custom
        
    Returns:
        AutoSkillTool: Configured AutoSkill Tool instance
    """
    return AutoSkillTool(isolation_level=isolation_level)
