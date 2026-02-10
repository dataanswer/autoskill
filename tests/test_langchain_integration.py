import os
import sys
import tempfile
import shutil
import pytest

# Add project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integrations.langchain_tool import create_auto_skill_tool
from integrations.toolkit import create_auto_skill_toolkit

class TestLangChainIntegration:
    """Test LangChain integration functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        # Create temporary directory as skill plugins directory
        self.temp_dir = tempfile.mkdtemp()
        # Create skill agent tool
        self.auto_skill_tool = create_auto_skill_tool(isolation_level="none")
        # Create skill agent toolkit
        self.auto_skill_toolkit = create_auto_skill_toolkit(isolation_level="none")
    
    def teardown_method(self):
        """Clean up test environment"""
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_skill_agent_tool(self):
        """Test create skill agent tool"""
        assert self.auto_skill_tool is not None
        assert hasattr(self.auto_skill_tool, "list_skills")
        assert hasattr(self.auto_skill_tool, "_run")
    
    def test_list_skills(self):
        """Test list skills"""
        import json
        skills_str = self.auto_skill_tool.list_skills()
        skills = json.loads(skills_str)
        assert isinstance(skills, list)
    
    def test_create_skill_agent_toolkit(self):
        """Test create skill agent toolkit"""
        assert self.auto_skill_toolkit is not None
        assert hasattr(self.auto_skill_toolkit, "get_tools")
        assert hasattr(self.auto_skill_toolkit, "refresh_tools")
    
    def test_get_tools(self):
        """Test get tools list"""
        tools = self.auto_skill_toolkit.get_tools()
        assert isinstance(tools, list)
    
    def test_refresh_tools(self):
        """Test refresh tools list"""
        tools = self.auto_skill_toolkit.refresh_tools()
        assert isinstance(tools, list)

if __name__ == "__main__":
    pytest.main([__file__])