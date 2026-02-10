#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoSkill Basic Usage Example

Demonstrates AutoSkill's core functionality:
1. Initialize AutoSkill
2. Create skills
3. Execute skills
4. Manage skills
"""

import os
import sys

# Add project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from AutoSkill import AutoSkill

def main():
    """Main function"""
    print("=" * 60)
    print("AutoSkill Basic Usage Example")
    print("=" * 60)
    
    # 1. Initialize AutoSkill
    print("\n1. Initializing AutoSkill...")
    auto_skill = AutoSkill(isolation_level="none")
    print("   ✓ AutoSkill initialized successfully")
    
    # 2. List all available skills
    print("\n2. Listing all available skills...")
    skills = auto_skill.list_skills()
    print(f"   ✓ Found {len(skills)} skills")
    for skill in skills:
        print(f"   - {skill['name']}: {skill.get('description', 'No description')}")
    
    # 3. Create a new skill
    print("\n3. Creating a new skill...")
    skill_name = "example_calculator"
    task_description = "Create a simple calculator skill that can perform basic mathematical operations"
    
    try:
        skill_path = auto_skill.create_skill(skill_name, task_description)
        print(f"   ✓ Skill created successfully: {skill_path}")
    except Exception as e:
        print(f"   ⚠ Skill creation failed (API key may be required): {e}")
        print("   💡 Tip: Please ensure you have set the AUTO_SKILL_API_KEY environment variable")
    
    # 4. Refresh skill list
    print("\n4. Refreshing skill list...")
    auto_skill.reload_skills()
    updated_skills = auto_skill.list_skills()
    print(f"   ✓ Skill list updated, now has {len(updated_skills)} skills")
    
    # 5. Execute skill (if calculator skill exists)
    print("\n5. Executing skill...")
    calculator_skill = next((skill for skill in updated_skills if skill['name'] == "calculator"), None)
    
    if calculator_skill:
        try:
            result = auto_skill.execute_skill("calculator", {"expression": "10 + 20"})
            print(f"   ✓ Skill executed successfully")
            print(f"   Execution result: {result}")
        except Exception as e:
            print(f"   ⚠ Skill execution failed: {e}")
    else:
        print("   ⚠ Calculator skill not found, skipping execution example")
    
    # 6. Get skill information
    print("\n6. Getting skill information...")
    if updated_skills:
        first_skill = updated_skills[0]
        skill_info = auto_skill.get_skill_info(first_skill['name'])
        print(f"   ✓ Skill information:")
        print(f"     Name: {skill_info.get('name', 'N/A')}")
        print(f"     Description: {skill_info.get('description', 'N/A')}")
        print(f"     Version: {skill_info.get('version', 'N/A')}")
        print(f"     Category: {skill_info.get('category', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("Example demonstration completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()