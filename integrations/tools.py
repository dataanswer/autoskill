from langchain_core.tools import Tool
from typing import Dict, Any, Optional
from __init__ import AutoSkill

class SkillTool(Tool):
    """技能工具，为每个技能创建一个单独的工具"""
    
    def __init__(self, skill_name: str, skill_info: Dict[str, Any], skill_agent: AutoSkill):
        """
        初始化技能工具
        
        Args:
            skill_name: 技能名称
            skill_info: 技能信息
            skill_agent: AutoSkill实例
        """
        super().__init__(
            name=skill_name,
            func=self._run,
            description=skill_info.get("description", "执行技能")
        )
        
        # 使用__dict__来绕过Pydantic的字段检查
        self.__dict__['skill_name'] = skill_name
        self.__dict__['skill_info'] = skill_info
        self.__dict__['skill_agent'] = skill_agent
    
    def _run(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行技能
        
        Args:
            parameters: 技能参数
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        skill_agent = self.__dict__.get('skill_agent')
        skill_name = self.__dict__.get('skill_name')
        
        if not skill_agent:
            return {"success": False, "error": "SkillTool not properly initialized: skill_agent is None"}
        
        if not skill_name:
            return {"success": False, "error": "SkillTool not properly initialized: skill_name is None"}
        
        try:
            if parameters is not None and not isinstance(parameters, dict):
                return {"success": False, "error": "parameters must be a dictionary"}
            
            result = skill_agent.execute_skill(skill_name, parameters or {})
            
            # 确保返回值是字典
            if not isinstance(result, dict):
                return {"success": True, "result": result}
            
            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"Error executing skill {skill_name}: {str(e)}"}


class SkillManagementTool(Tool):
    """技能管理工具，用于管理技能"""
    
    def __init__(self, skill_agent: AutoSkill):
        """
        初始化技能管理工具
        
        Args:
            skill_agent: AutoSkill实例
        """
        super().__init__(
            name="skill_management",
            func=self._run,
            description="管理技能，包括创建、列出、获取信息等操作"
        )
        
        # 使用__dict__来绕过Pydantic的字段检查
        self.__dict__['skill_agent'] = skill_agent
    
    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        执行技能管理操作
        
        Args:
            action: 操作类型，可选值：list, info, create, reload
            **kwargs: 操作参数
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        skill_agent = self.__dict__.get('skill_agent')
        
        if not skill_agent:
            return {"success": False, "error": "skill_agent not initialized"}
        
        try:
            if not action:
                return {"success": False, "error": "action is required"}
            
            if action == "list":
                try:
                    skills = skill_agent.list_skills()
                    return {"success": True, "skills": skills}
                except Exception as e:
                    return {"success": False, "error": f"Failed to list skills: {str(e)}"}
            elif action == "info":
                skill_name = kwargs.get("skill_name")
                if not skill_name:
                    return {"success": False, "error": "skill_name is required"}
                try:
                    skill_info = skill_agent.get_skill_info(skill_name)
                    return skill_info
                except Exception as e:
                    return {"success": False, "error": f"Failed to get skill info: {str(e)}"}
            elif action == "create":
                skill_name = kwargs.get("skill_name")
                task_description = kwargs.get("task_description")
                template = kwargs.get("template")
                
                if not skill_name:
                    return {"success": False, "error": "skill_name is required"}
                
                if not task_description:
                    return {"success": False, "error": "task_description is required"}
                
                try:
                    result = skill_agent.create_skill(skill_name, task_description, template)
                    return {"success": True, "skill_path": result}
                except Exception as e:
                    return {"success": False, "error": f"Failed to create skill: {str(e)}"}
            elif action == "reload":
                try:
                    message = skill_agent.reload_skills()
                    return {"success": True, "message": message}
                except Exception as e:
                    return {"success": False, "error": f"Failed to reload skills: {str(e)}"}
            else:
                return {"success": False, "error": f"Unknown action: {action}, supported actions: list, info, create, reload"}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"Failed to execute management action: {str(e)}"}
