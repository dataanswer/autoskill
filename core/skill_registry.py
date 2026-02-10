from typing import Dict, List, Any

class SkillRegistry:
    def __init__(self):
        self.skills: Dict[str, Dict[str, Any]] = {}
    
    def register_skill(self, skill_name: str, metadata: Dict[str, Any]):
        self.skills[skill_name] = metadata
    
    def get_skill(self, skill_name: str) -> Dict[str, Any]:
        return self.skills.get(skill_name, {})
    
    def get_all_skills(self) -> List[Dict[str, Any]]:
        return list(self.skills.values())
    
    def clear(self):
        self.skills.clear()
    
    def exists(self, skill_name: str) -> bool:
        return skill_name in self.skills
    
    def update_skill(self, skill_name: str, metadata: Dict[str, Any]):
        if skill_name in self.skills:
            self.skills[skill_name].update(metadata)
    
    def remove_skill(self, skill_name: str):
        if skill_name in self.skills:
            del self.skills[skill_name]
