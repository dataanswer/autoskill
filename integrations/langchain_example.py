import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from integrations.langchain_tool import create_skill_agent_tool
from integrations.toolkit import create_skill_agent_toolkit

# 初始化Skill Agent Tool
skill_agent_tool = create_skill_agent_tool(isolation_level="venv")

# 初始化Skill Agent Toolkit（动态工具管理）
skill_agent_toolkit = create_skill_agent_toolkit(isolation_level="venv")

# 初始化LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 定义提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个智能助手，能够使用Skill Agent插件来创建和执行技能。
    
    当用户需要执行特定任务时，你可以：
    1. 检查是否存在相关的现有技能
    2. 如果存在，使用execute操作执行该技能
    3. 如果不存在，使用create操作创建一个新技能，然后执行它
    
    请根据用户的请求，生成适当的JSON格式参数来调用AutoSkill工具。
    """),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 创建工具列表
tools = [skill_agent_tool]

# 创建Agent
agent = create_openai_functions_agent(llm, tools, prompt)

# 创建Agent Executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 示例1：执行现有技能（假设存在calculator技能）
def execute_existing_skill():
    print("\n=== 示例1：执行现有技能 ===")
    try:
        response = agent_executor.invoke(
            {"input": "使用计算器技能计算 100 + 200"}
        )
        print(f"响应: {response['output']}")
    except Exception as e:
        print(f"错误: {str(e)}")

# 示例2：创建新技能
def create_and_execute_skill():
    print("\n=== 示例2：创建新技能 ===")
    try:
        response = agent_executor.invoke(
            {"input": "创建一个天气查询技能，输入城市名称，返回该城市的当前天气。技能名称为weather_checker"}
        )
        print(f"响应: {response['output']}")
    except Exception as e:
        print(f"错误: {str(e)}")

# 示例3：列出所有可用技能
def list_available_skills():
    print("\n=== 示例3：列出所有可用技能 ===")
    skills = skill_agent_tool.list_skills()
    print(f"可用技能: {skills}")

# 示例4：使用动态工具管理

def use_dynamic_tool_management():
    print("\n=== 示例4：使用动态工具管理 ===")
    try:
        # 获取初始工具列表
        initial_tools = skill_agent_toolkit.get_tools()
        print(f"初始工具数量: {len(initial_tools)}")
        print(f"初始工具列表: {[tool.name for tool in initial_tools]}")
        
        # 创建一个新技能
        print("\n创建新技能...")
        from AutoSkill import AutoSkill
        auto_skill = AutoSkill(isolation_level="venv")
        auto_skill.create_skill(
            "weather_checker",
            "创建一个天气查询技能，输入城市名称，返回该城市的当前天气"
        )
        
        # 刷新工具列表
        print("\n刷新工具列表...")
        refreshed_tools = skill_agent_toolkit.refresh_tools()
        print(f"刷新后工具数量: {len(refreshed_tools)}")
        print(f"刷新后工具列表: {[tool.name for tool in refreshed_tools]}")
        
        # 检查新技能是否已添加为工具
        weather_tool = next((tool for tool in refreshed_tools if tool.name == "weather_checker"), None)
        if weather_tool:
            print("\n✓ 新技能已自动添加为工具")
            print(f"  工具描述: {weather_tool.description}")
        else:
            print("\n✗ 新技能未添加为工具")
            
    except Exception as e:
        print(f"错误: {str(e)}")


# 运行示例
if __name__ == "__main__":
    print("开始Langchain Agent与Skill Agent插件集成示例")
    
    # 列出所有可用技能
    list_available_skills()
    
    # 执行现有技能
    execute_existing_skill()
    
    # 创建并执行新技能
    create_and_execute_skill()
    
    # 使用动态工具管理
    use_dynamic_tool_management()
    
    print("示例运行完成")
