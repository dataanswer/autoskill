import argparse
import json
import sys
import os

# Import from autoskill package
from autoskill import AutoSkill, AutoSkillError

def list_skills(auto_skill):
    """List all available skills"""
    try:
        skills = auto_skill.list_skills()
        print("=== Available Skills ===")
        for skill in skills:
            if isinstance(skill, dict):
                name = skill.get('name', 'Unknown')
                description = skill.get('description', 'No description')
                version = skill.get('version', '1.0.0')
                print(f"- {name} (v{version}): {description}")
            else:
                print(f"- {skill}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def execute_skill(auto_skill, skill_name, parameters):
    """Execute specified skill"""
    try:
        # Parse parameters
        if parameters:
            try:
                # Try direct parsing
                params = json.loads(parameters)
            except json.JSONDecodeError:
                # Try to handle PowerShell format parameters
                try:
                    # Remove outer quotes
                    if parameters.startswith("'") and parameters.endswith("'"):
                        params_str = parameters[1:-1]
                    else:
                        params_str = parameters
                    params = json.loads(params_str)
                except json.JSONDecodeError:
                    print("Error: Invalid parameter format, please use JSON format")
                    sys.exit(1)
        else:
            params = {}
        
        print(f"Executing skill: {skill_name}")
        print(f"Parameters: {params}")
        
        result = auto_skill.execute_skill(skill_name, params)
        print("=== Execution Result ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except AutoSkillError as e:
        print(f"Error: [{e.error_code}] {e.message}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def create_skill(auto_skill, skill_name, description, template):
    """Create new skill"""
    try:
        print(f"Creating skill: {skill_name}")
        print(f"Description: {description}")
        if template:
            print(f"Template: {template}")
        
        result = auto_skill.create_skill(skill_name, description, template)
        print("=== Creation Result ===")
        print(result)
    except AutoSkillError as e:
        print(f"Error: [{e.error_code}] {e.message}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def get_skill_info(auto_skill, skill_name):
    """Get skill information"""
    try:
        info = auto_skill.get_skill_info(skill_name)
        print(f"=== Skill Information: {skill_name} ===")
        print(json.dumps(info, indent=2, ensure_ascii=False))
    except AutoSkillError as e:
        print(f"Error: [{e.error_code}] {e.message}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def delete_skill(auto_skill, skill_name):
    """Delete skill"""
    try:
        result = auto_skill.delete_skill(skill_name)
        print(f"=== Deletion Result ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def reload_skills(auto_skill):
    """Reload skills"""
    try:
        result = auto_skill.reload_skills()
        print(f"=== Reload Result ===")
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def check_version():
    """Check version information"""
    version_info = AutoSkill.get_version()
    print("=== Version Information ===")
    print(f"AutoSkill version: {version_info['version']}")
    print(f"Minimum Python version: {version_info['min_python_version']}")
    print(f"Supported LangChain version: {version_info['supported_langchain_version']}")
    
    # Check compatibility
    compatibility = AutoSkill.check_compatibility()
    print("\n=== Compatibility Check ===")
    print(f"Python: {compatibility['python']['current']} (required {compatibility['python']['required']}) - {'Compatible' if compatibility['python']['compatible'] else 'Incompatible'}")
    print(f"LangChain: {compatibility['langchain']['current'] or 'Not installed'} (required {compatibility['langchain']['required']}) - {'Compatible' if compatibility['langchain']['compatible'] else 'Incompatible'}")
    if not compatibility['langchain']['compatible'] and compatibility['langchain']['error']:
        print(f"LangChain error: {compatibility['langchain']['error']}")
    print(f"Overall compatibility: {'Compatible' if compatibility['overall_compatible'] else 'Incompatible'}")

def main():
    """CLI main function"""
    parser = argparse.ArgumentParser(description='AutoSkill CLI Tool')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List all available skills')
    
    # execute command
    execute_parser = subparsers.add_parser('execute', help='Execute specified skill')
    execute_parser.add_argument('skill_name', help='Skill name')
    execute_parser.add_argument('--params', help='Execution parameters (JSON format)')
    
    # create command
    create_parser = subparsers.add_parser('create', help='Create new skill')
    create_parser.add_argument('skill_name', help='Skill name')
    create_parser.add_argument('description', help='Skill description')
    create_parser.add_argument('--template', help='Template name to use')
    
    # info command
    info_parser = subparsers.add_parser('info', help='Get skill information')
    info_parser.add_argument('skill_name', help='Skill name')
    
    # delete command
    delete_parser = subparsers.add_parser('delete', help='Delete skill')
    delete_parser.add_argument('skill_name', help='Skill name')
    
    # reload command
    reload_parser = subparsers.add_parser('reload', help='Reload skills')
    
    # version command
    version_parser = subparsers.add_parser('version', help='Check version information')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command specified, show help
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Create AutoSkill instance
    try:
        auto_skill = AutoSkill()
    except Exception as e:
        print(f"Failed to initialize AutoSkill: {e}")
        sys.exit(1)
    
    # Execute command
    if args.command == 'list':
        list_skills(auto_skill)
    elif args.command == 'execute':
        execute_skill(auto_skill, args.skill_name, args.params)
    elif args.command == 'create':
        create_skill(auto_skill, args.skill_name, args.description, args.template)
    elif args.command == 'info':
        get_skill_info(auto_skill, args.skill_name)
    elif args.command == 'delete':
        delete_skill(auto_skill, args.skill_name)
    elif args.command == 'reload':
        reload_skills(auto_skill)
    elif args.command == 'version':
        check_version()

if __name__ == '__main__':
    main()
