import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from integrations.langchain_tool import create_skill_agent_tool

"""
完整的技能创建和执行流程演示

包括以下步骤：
1. 用户意图分析
2. 技能规划
3. 技能实现
4. 技能执行
5. 技能反思
6. 技能优化和再次执行

这个演示展示了 Skill Agent 插件的完整工作流程，从用户意图到技能执行和反思优化的全过程。
"""

# 初始化 Skill Agent Tool
skill_agent_tool = create_skill_agent_tool(isolation_level="none")

# 初始化 LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 定义提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手，能够使用 Skill Agent 插件来创建和执行技能。"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 创建工具列表
tools = [skill_agent_tool]

# 创建 Agent 和 Agent Executor
get_agent = lambda: create_openai_functions_agent(llm, tools, prompt)
agent = get_agent()
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 演示完整流程
def complete_skill_demo():
    print("====================================")
    print("完整技能创建和执行流程演示")
    print("====================================")
    print()
    
    # 1. 用户意图分析
    print("=== 步骤 1: 用户意图分析 ===")
    user_intent = "我需要一个技能来分析销售数据，计算月度销售总额和平均销售额，并生成简单的销售趋势分析。"
    print(f"用户意图: {user_intent}")
    print()
    
    # 2. 技能规划和实现
    print("=== 步骤 2: 技能规划和实现 ===")
    print("系统正在分析用户意图，规划技能实现方案...")
    print()
    
    # 3. 技能创建和执行
    print("=== 步骤 3: 技能创建和执行 ===")
    print("系统正在创建销售数据分析技能...")
    
    # 执行任务，触发技能创建
    input_text = "创建一个销售数据分析技能，能够接收销售数据列表，计算月度销售总额和平均销售额，并生成简单的销售趋势分析。"
    result = agent_executor.invoke({"input": input_text})
    
    print("技能创建完成！")
    print()
    
    # 4. 技能执行
    print("=== 步骤 4: 技能执行 ===")
    print("系统正在执行销售数据分析技能...")
    
    # 准备测试数据
    sales_data = [
        {"month": "2024-01", "amount": 10000},
        {"month": "2024-02", "amount": 15000},
        {"month": "2024-03", "amount": 12000},
        {"month": "2024-04", "amount": 18000},
        {"month": "2024-05", "amount": 20000}
    ]
    
    # 执行技能
    input_text = f"使用销售数据分析技能分析以下数据：{sales_data}"
    result = agent_executor.invoke({"input": input_text})
    
    print("技能执行完成！")
    print()
    
    # 5. 技能反思和优化
    print("=== 步骤 5: 技能反思和优化 ===")
    print("系统正在反思技能执行结果，寻找优化空间...")
    
    # 触发技能反思和优化
    input_text = "优化销售数据分析技能，添加数据可视化功能，生成月度销售趋势图表，并计算销售增长率。"
    result = agent_executor.invoke({"input": input_text})
    
    print("技能优化完成！")
    print()
    
    # 6. 技能再次执行
    print("=== 步骤 6: 技能再次执行 ===")
    print("系统正在使用优化后的技能再次执行任务...")
    
    # 再次执行技能
    input_text = f"使用优化后的销售数据分析技能分析以下数据：{sales_data}"
    result = agent_executor.invoke({"input": input_text})
    
    print("技能再次执行完成！")
    print()
    
    print("====================================")
    print("完整流程演示完成！")
    print("====================================")

if __name__ == "__main__":
    complete_skill_demo()
