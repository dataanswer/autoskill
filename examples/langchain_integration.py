#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoSkill LangChain Integration Example

Demonstrates how to integrate AutoSkill with LangChain Agent
"""

import os
import sys

# Add project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

from integrations.langchain_tool import create_auto_skill_tool

def main():
    """Main function"""
    load_dotenv()
    
    print("=" * 60)
    print("AutoSkill LangChain Integration Example")
    print("=" * 60)
    
    # 1. Initialize LLM
    print("\n1. Initializing LLM...")
    llm = ChatOpenAI(
        model=os.getenv("AUTO_SKILL_MODEL", "gpt-3.5-turbo"),
        temperature=0,
        api_key=os.getenv("AUTO_SKILL_API_KEY"),
        base_url=os.getenv("AUTO_SKILL_BASE_URL")
    )
    print("   ✓ LLM initialized successfully")
    
    # 2. Create AutoSkill tool
    print("\n2. Creating AutoSkill tool...")
    auto_skill_tool = create_auto_skill_tool(isolation_level="none")
    print("   ✓ AutoSkill tool created successfully")
    
    # 3. Define prompt template
    print("\n3. Defining prompt template...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", '''You are an intelligent assistant that can use the AutoSkill plugin to create and execute skills.
        
        When a user needs to perform a specific task, you can:
        1. Check if a relevant existing skill exists
        2. If it exists, use the execute operation to run the skill
        3. If it doesn't exist, use the create operation to create a new skill and then execute it
        
        Please generate appropriate JSON format parameters to call the AutoSkill tool based on the user's request.
        '''),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    print("   ✓ Prompt template created successfully")
    
    # 4. Create Agent
    print("\n4. Creating Agent...")
    agent = create_openai_functions_agent(llm, [auto_skill_tool], prompt)
    print("   ✓ Agent created successfully")
    
    # 5. Create Agent Executor
    print("\n5. Creating Agent Executor...")
    agent_executor = AgentExecutor(agent=agent, tools=[auto_skill_tool], verbose=True)
    print("   ✓ Agent Executor created successfully")
    
    # 6. Example: Using calculator skill
    print("\n6. Example: Using calculator skill...")
    try:
        response = agent_executor.invoke({
            "input": "Use the calculator skill to calculate 100 + 200"
        })
        print(f"   ✓ Agent response: {response['output']}")
    except Exception as e:
        print(f"   ⚠ Execution failed: {e}")
    
    # 7. Example: Creating new skill
    print("\n7. Example: Creating new skill...")
    try:
        response = agent_executor.invoke({
            "input": "Create a weather query skill that takes a city name as input and returns the current weather for that city"
        })
        print(f"   ✓ Agent response: {response['output']}")
    except Exception as e:
        print(f"   ⚠ Execution failed: {e}")
    
    print("\n" + "=" * 60)
    print("Integration example demonstration completed!")
    print("=" * 60)
    print("\n💡 Tips:")
    print("   - Ensure you have set the AUTO_SKILL_API_KEY environment variable")
    print("   - You can set it through a .env file or directly as an environment variable")
    print("   - For more information, please refer to README.md")

if __name__ == "__main__":
    main()