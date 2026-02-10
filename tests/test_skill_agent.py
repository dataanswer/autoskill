import os
import sys
import tempfile
import shutil
import pytest

# Add project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from __init__ import AutoSkill, AutoSkillError

class TestAutoSkill:
    """Test AutoSkill core functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        # Create temporary directory as skill plugins directory
        self.temp_dir = tempfile.mkdtemp()
        # Initialize AutoSkill with temporary directory
        self.skill_agent = AutoSkill(
            config={
                "skills": {
                    "plugins_dir": self.temp_dir
                }
            },
            isolation_level="none"
        )
    
    def teardown_method(self):
        """Clean up test environment"""
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_list_skills_initial(self):
        """Test initial skill list"""
        skills = self.skill_agent.list_skills()
        assert isinstance(skills, list)
    
    def test_create_skill(self):
        """Test create skill"""
        # Create a simple skill
        skill_name = "test_skill"
        task_description = "Create a test skill that returns 'Hello, World!'"
        
        result = self.skill_agent.create_skill(skill_name, task_description)
        assert isinstance(result, str)
        assert os.path.exists(result)
        
        # Verify skill has been added to skill list
        skills = self.skill_agent.list_skills()
        skill_names = [skill.get("name") for skill in skills]
        assert skill_name in skill_names
    
    def test_execute_skill(self):
        """Test execute skill"""
        # Create a simple skill
        skill_name = "test_skill"
        task_description = "Create a test skill that receives name parameter and returns 'Hello, {name}!'"
        
        self.skill_agent.create_skill(skill_name, task_description)
        
        # Execute skill
        parameters = {"name": "Test"}
        result = self.skill_agent.execute_skill(skill_name, parameters)
        
        assert isinstance(result, dict)
        assert result.get("success", False) is True
    
    def test_execute_nonexistent_skill(self):
        """Test execute non-existent skill"""
        with pytest.raises(AutoSkillError):
            self.skill_agent.execute_skill("nonexistent_skill", {})
    
    def test_reload_skills(self):
        """Test reload skills"""
        result = self.skill_agent.reload_skills()
        assert isinstance(result, str)
    
    def test_get_skill_info(self):
        """Test get skill information"""
        # Create a simple skill
        skill_name = "test_skill"
        task_description = "Create a test skill"
        
        self.skill_agent.create_skill(skill_name, task_description)
        
        # Get skill information
        skill_info = self.skill_agent.get_skill_info(skill_name)
        assert isinstance(skill_info, dict)
        assert skill_info.get("name") == skill_name
    
    def test_get_nonexistent_skill_info(self):
        """Test get non-existent skill information"""
        with pytest.raises(AutoSkillError):
            self.skill_agent.get_skill_info("nonexistent_skill")
    
    def test_set_isolation_level(self):
        """Test set environment isolation level"""
        # Set isolation level to venv
        self.skill_agent.set_isolation_level("venv")
        assert self.skill_agent.get_isolation_level() == "venv"
        
        # Set isolation level to none
        self.skill_agent.set_isolation_level("none")
        assert self.skill_agent.get_isolation_level() == "none"
    
    @classmethod
    def test_get_version(cls):
        """Test get version information"""
        version_info = AutoSkill.get_version()
        assert isinstance(version_info, dict)
        assert "version" in version_info
        assert "min_python_version" in version_info
        assert "supported_langchain_version" in version_info
    
    def test_check_compatibility(self):
        """Test check compatibility"""
        compatibility = AutoSkill.check_compatibility()
        assert isinstance(compatibility, dict)
        assert "python" in compatibility
        assert "langchain" in compatibility
        assert "overall_compatible" in compatibility

if __name__ == "__main__":
    pytest.main([__file__])