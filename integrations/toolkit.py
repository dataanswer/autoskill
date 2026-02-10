from typing import List
from langchain_core.tools import Tool
from __init__ import AutoSkill
from .tools import SkillTool, SkillManagementTool

class AutoSkillToolkit:
    """
    AutoSkill 工具包，用于管理所有技能工具
    
    提供动态技能管理功能，包括：
    1. 为每个现有技能创建单独的工具
    2. 提供技能管理工具，用于创建、列出、获取技能信息
    3. 支持动态刷新工具列表，使新创建的技能立即可用
    """
    
    def __init__(self, skill_agent: AutoSkill):
        """
        初始化工具包
        
        Args:
            skill_agent: AutoSkill实例
        """
        self.skill_agent = skill_agent
    
    def get_tools(self) -> List[Tool]:
        """
        获取所有技能工具
        
        Returns:
            List[Tool]: 包含所有技能工具的列表
        """
        tools = []
        
        try:
            # 添加技能管理工具
            tools.append(SkillManagementTool(self.skill_agent))
            
            # 添加每个技能对应的工具
            try:
                skills = self.skill_agent.list_skills()
                for skill_info in skills:
                    try:
                        skill_name = skill_info.get("name")
                        if skill_name:
                            tool = SkillTool(skill_name, skill_info, self.skill_agent)
                            tools.append(tool)
                    except Exception as e:
                        print(f"警告: 创建技能工具失败: {str(e)}")
                        continue
            except Exception as e:
                print(f"警告: 获取技能列表失败: {str(e)}")
                
        except Exception as e:
            print(f"错误: 获取工具列表失败: {str(e)}")
            
        return tools
    
    def refresh_tools(self) -> List[Tool]:
        """
        刷新工具列表
        
        重新加载技能并生成工具列表，使新创建的技能立即可用
        
        Returns:
            List[Tool]: 刷新后的工具列表
        """
        # 重新加载技能
        self.skill_agent.reload_skills()
        # 重新生成工具
        return self.get_tools()


def create_auto_skill_toolkit(isolation_level: str = "none") -> AutoSkillToolkit:
    """
    创建AutoSkill Toolkit的便捷函数
    
    Args:
        isolation_level: 环境隔离级别，可选值：none, venv, custom
        
    Returns:
        AutoSkillToolkit: 配置好的AutoSkill Toolkit实例
    """
    skill_agent = AutoSkill(isolation_level=isolation_level)
    return AutoSkillToolkit(skill_agent)
