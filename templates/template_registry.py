import os
import yaml
from typing import Dict, List, Optional

class TemplateRegistry:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.templates: Dict[str, str] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize templates"""
        # Ensure template directory exists
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Load built-in templates
        self._load_builtin_templates()
        
        # Load user-defined templates
        self._load_user_templates()
    
    def _load_builtin_templates(self):
        """Load built-in templates"""
        # Built-in templates (YAML format)
        builtin_templates = {
            "base_skill": {
                "name": "base_skill",
                "description": "Base skill template",
                "content": """# Base Skill Template

            This is a base skill template for generating general skill plugins.

            Core requirements:
            1. Must contain execute function that receives parameters
            2. Return format must be {"success": bool, "result": any}
            3. Use compatible Python 3.8+ syntax
            4. Code should be concise, clear, and functionally complete
            """
            },
            "data_analysis": {
                "name": "data_analysis",
                "description": "Data analysis skill template",
                "content": """# Data Analysis Skill Template

            This is a data analysis skill template for generating data analysis related skill plugins.

            Core requirements:
            1. Support basic data loading and preprocessing
            2. Provide common data analysis functions
            3. Support result visualization (optional)
            4. Use data analysis libraries like pandas, numpy
            """
            }
        }
        
        # Save built-in templates
        for name, template_data in builtin_templates.items():
            template_path = os.path.join(self.templates_dir, f"{name}.yaml")
            if not os.path.exists(template_path):
                with open(template_path, 'w', encoding='utf-8') as f:
                    yaml.dump(template_data, f, allow_unicode=True, sort_keys=False)
            self.templates[name] = template_data["content"]
    
    def _load_user_templates(self):
        """Load user-defined templates"""
        if not os.path.exists(self.templates_dir):
            return
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.yaml'):
                template_name = filename[:-5]
                template_path = os.path.join(self.templates_dir, filename)
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                if template_data and "content" in template_data:
                    self.templates[template_name] = template_data["content"]
    
    def get_template(self, template_name: str) -> Optional[str]:
        """Get template content"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """List all available templates"""
        return list(self.templates.keys())
    
    def add_template(self, template_name: str, content: str, description: str = "") -> bool:
        """Add new template"""
        try:
            template_data = {
                "name": template_name,
                "description": description,
                "content": content
            }
            template_path = os.path.join(self.templates_dir, f"{template_name}.yaml")
            with open(template_path, 'w', encoding='utf-8') as f:
                yaml.dump(template_data, f, allow_unicode=True, sort_keys=False)
            self.templates[template_name] = content
            return True
        except Exception as e:
            print(f"Failed to add template: {e}")
            return False
    
    def update_template(self, template_name: str, content: str, description: str = "") -> bool:
        """Update template"""
        if template_name not in self.templates:
            return False
        
        try:
            template_data = {
                "name": template_name,
                "description": description,
                "content": content
            }
            template_path = os.path.join(self.templates_dir, f"{template_name}.yaml")
            with open(template_path, 'w', encoding='utf-8') as f:
                yaml.dump(template_data, f, allow_unicode=True, sort_keys=False)
            self.templates[template_name] = content
            return True
        except Exception as e:
            print(f"Failed to update template: {e}")
            return False
    
    def delete_template(self, template_name: str) -> bool:
        """Delete template"""
        if template_name not in self.templates:
            return False
        
        try:
            template_path = os.path.join(self.templates_dir, f"{template_name}.yaml")
            if os.path.exists(template_path):
                os.remove(template_path)
            del self.templates[template_name]
            return True
        except Exception as e:
            print(f"Failed to delete template: {e}")
            return False
    
    def reload_templates(self):
        """Reload templates"""
        self.templates.clear()
        self._initialize_templates()
        return f"Reloaded {len(self.templates)} templates"
