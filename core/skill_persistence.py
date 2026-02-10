"""Skill persistence manager, responsible for saving and loading skills"""

import json
import os
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime

class SkillPersistence:
    """Skill persistence manager"""
    
    def __init__(self, storage_dir: str = "skills/plugins"):
        """
        Initialize skill persistence manager
        
        Args:
            storage_dir: Skill storage directory
        """
        self.storage_dir = storage_dir
        self.versions_file = os.path.join(storage_dir, "skill_versions.json")
        
        # Ensure storage directory exists
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize versions file
        self._init_versions_file()
    
    def _init_versions_file(self):
        """Initialize versions file"""
        if not os.path.exists(self.versions_file):
            self._save_json(self.versions_file, {})
    
    def _save_json(self, file_path: str, data: Dict[str, Any]):
        """Save JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load JSON file"""
        if not os.path.exists(file_path):
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _read_file(self, file_path: str) -> str:
        """Read file content"""
        if not os.path.exists(file_path):
            return ""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _save_file(self, file_path: str, content: str):
        """Save file content"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def save_skill_version(self, skill_name: str, version: str, description: str = "") -> bool:
        """
        Save skill version
        
        Args:
            skill_name: Skill name
            version: Version number
            description: Version description
            
        Returns:
            Whether save was successful
        """
        try:
            skill_dir = os.path.join(self.storage_dir, skill_name)
            
            if not os.path.exists(skill_dir):
                return False
            
            # Read skill.py and manifest.yaml
            skill_code = self._read_file(os.path.join(skill_dir, "skill.py"))
            manifest_content = self._read_file(os.path.join(skill_dir, "manifest.yaml"))
            requirements_content = self._read_file(os.path.join(skill_dir, "requirements.txt"))
            
            # Load existing versions
            versions = self._load_json(self.versions_file)
            
            if skill_name not in versions:
                versions[skill_name] = []
            
            # Check if version already exists
            existing_version = None
            for v in versions[skill_name]:
                if v["version"] == version:
                    existing_version = v
                    break
            
            # If version exists, update it
            if existing_version:
                existing_version["code"] = skill_code
                existing_version["manifest"] = manifest_content
                existing_version["requirements"] = requirements_content
                existing_version["description"] = description
                existing_version["updated_at"] = datetime.now().isoformat()
            else:
                # Add new version
                version_record = {
                    "version": version,
                    "code": skill_code,
                    "manifest": manifest_content,
                    "requirements": requirements_content,
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                versions[skill_name].append(version_record)
            
            self._save_json(self.versions_file, versions)
            return True
        except Exception as e:
            print(f"Failed to save skill version: {e}")
            return False
    
    def get_skill_versions(self, skill_name: str) -> List[Dict[str, Any]]:
        """
        Get all versions of skill
        
        Args:
            skill_name: Skill name
            
        Returns:
            List of versions
        """
        try:
            versions = self._load_json(self.versions_file)
            return versions.get(skill_name, [])
        except Exception as e:
            print(f"Failed to get skill versions: {e}")
            return []
    
    def restore_skill_version(self, skill_name: str, version: str) -> bool:
        """
        Restore skill to specified version
        
        Args:
            skill_name: Skill name
            version: Version number
            
        Returns:
            Whether restore was successful
        """
        try:
            versions = self._load_json(self.versions_file)
            
            if skill_name not in versions:
                return False
            
            # Find specified version
            version_record = None
            for v in versions[skill_name]:
                if v["version"] == version:
                    version_record = v
                    break
            
            if not version_record:
                return False
            
            # Restore files
            skill_dir = os.path.join(self.storage_dir, skill_name)
            self._save_file(os.path.join(skill_dir, "skill.py"), version_record["code"])
            self._save_file(os.path.join(skill_dir, "manifest.yaml"), version_record["manifest"])
            
            if version_record["requirements"]:
                self._save_file(os.path.join(skill_dir, "requirements.txt"), version_record["requirements"])
            
            return True
        except Exception as e:
            print(f"Failed to restore skill version: {e}")
            return False
    
    def _increment_version(self, version: str) -> str:
        """
        Increment version number
        
        Args:
            version: Current version number (e.g., "1.0.0")
            
        Returns:
            New version number (e.g., "1.0.1")
        """
        try:
            parts = version.split('.')
            if len(parts) == 2:
                major, minor = int(parts[0]), int(parts[1])
                return f"{major}.{minor + 1}"
            elif len(parts) == 3:
                major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
                return f"{major}.{minor}.{patch + 1}"
            return version
        except:
            return version
    
    def update_skill_version(self, skill_name: str, description: str = "") -> str:
        """
        Update skill version
        
        Args:
            skill_name: Skill name
            description: Version description
            
        Returns:
            New version number
        """
        try:
            # Read current version
            skill_dir = os.path.join(self.storage_dir, skill_name)
            manifest_path = os.path.join(skill_dir, "manifest.yaml")
            
            if not os.path.exists(manifest_path):
                return "1.0.0"
            
            manifest_content = self._read_file(manifest_path)
            import yaml
            manifest = yaml.safe_load(manifest_content)
            
            # Check if manifest is None
            if manifest is None:
                return "1.0.0"
            
            current_version = manifest.get("version", "1.0.0")
            
            # Save current version
            self.save_skill_version(skill_name, current_version, description)
            
            # Increment version number
            new_version = self._increment_version(current_version)
            
            # Update version number in manifest.yaml
            manifest["version"] = new_version
            self._save_file(manifest_path, yaml.dump(manifest, default_flow_style=False, allow_unicode=True))
            
            # Save new version to version history
            self.save_skill_version(skill_name, new_version, description)
            
            return new_version
        except Exception as e:
            print(f"Failed to update skill version: {e}")
            return "1.0.0"
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """
        List all skills
        
        Returns:
            List of skill information
        """
        try:
            skill_list = []
            
            if not os.path.exists(self.storage_dir):
                return skill_list
            
            for skill_name in os.listdir(self.storage_dir):
                skill_dir = os.path.join(self.storage_dir, skill_name)
                
                if not os.path.isdir(skill_dir):
                    continue
                
                manifest_path = os.path.join(skill_dir, "manifest.yaml")
                if not os.path.exists(manifest_path):
                    continue
                
                try:
                    manifest_content = self._read_file(manifest_path)
                    import yaml
                    manifest = yaml.safe_load(manifest_content)
                    
                    skill_info = {
                        "name": skill_name,
                        "description": manifest.get("description", ""),
                        "version": manifest.get("version", "1.0.0"),
                        "created_at": manifest.get("created_at", ""),
                        "last_used": manifest.get("last_used", ""),
                        "usage_count": manifest.get("usage_count", 0)
                    }
                    skill_list.append(skill_info)
                except:
                    continue
            
            return skill_list
        except Exception as e:
            print(f"Failed to list skills: {e}")
            return []
