import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from core.skill_persistence import SkillPersistence

class SkillGenerator:
    def __init__(self, plugins_dir: str = "skills/plugins"):
        """
        Initialize skill generator
        
        Args:
            plugins_dir: Plugin directory path, defaults to "skills/plugins"
        """
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.persistence = SkillPersistence(str(plugins_dir))
    
    def generate_skill(self, skill_name: str, description: str, code: str, 
                      parameters: Dict = None, dependencies: List[str] = None) -> str:
        """
        Generate skill
        
        Args:
            skill_name: Skill name
            description: Skill description
            code: Skill code
            parameters: Skill parameter definition, defaults to empty object
            dependencies: Skill dependency list, defaults to empty list
            
        Returns:
            str: Generated skill path
        """
        skill_path = self.plugins_dir / skill_name
        skill_path.mkdir(parents=True, exist_ok=True)
        
        if parameters is None:
            parameters = {
                "type": "object",
                "properties": {}
            }
        
        if dependencies is None:
            dependencies = []
        
        manifest = {
            "name": skill_name,
            "version": "1.0.0",
            "description": description,
            "category": "general",
            "parameters": parameters,
            "environment": {
                "dependencies": dependencies
            }
        }
        
        with open(skill_path / "manifest.yaml", "w", encoding="utf-8") as f:
            yaml.dump(manifest, f, allow_unicode=True, sort_keys=False)
        
        with open(skill_path / "skill.py", "w", encoding="utf-8") as f:
            f.write(code)
        
        if dependencies:
            with open(skill_path / "requirements.txt", "w", encoding="utf-8") as f:
                for dep in dependencies:
                    f.write(f"{dep}\n")
        
        # Save skill version information
        self.persistence.save_skill_version(skill_name, "1.0.0", f"Initial version of {skill_name}")
        
        return str(skill_path)
