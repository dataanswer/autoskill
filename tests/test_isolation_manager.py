#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test environment isolation management module
"""

import os
import sys
import tempfile
import pytest

# Add project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.isolation_manager import IsolationManager


class TestIsolationManager:
    """Test environment isolation manager"""
    
    def setup_method(self):
        """Set up test environment"""
        # Create temporary directory as virtual environment base directory
        self.temp_dir = tempfile.mkdtemp()
        self.manager = IsolationManager(base_dir=self.temp_dir)
        self.test_env_name = "test_env"
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_virtualenv(self):
        """Test create virtual environment"""
        # Create virtual environment
        env_path = self.manager.create_virtualenv(self.test_env_name)
        assert isinstance(env_path, str)
        assert os.path.exists(env_path)
        
        # Call again, should return the same path
        env_path2 = self.manager.create_virtualenv(self.test_env_name)
        assert env_path2 == env_path
    
    def test_get_venv_python(self):
        """Test get virtual environment Python executable path"""
        # Create virtual environment
        self.manager.create_virtualenv(self.test_env_name)
        
        # Get Python executable path
        python_exe = self.manager.get_venv_python(self.test_env_name)
        assert isinstance(python_exe, str)
        assert os.path.exists(python_exe)
        
        # Test non-existent virtual environment
        python_exe_nonexistent = self.manager.get_venv_python("nonexistent_env")
        assert python_exe_nonexistent is None
    
    def test_install_dependencies(self):
        """Test install dependencies in virtual environment"""
        # Create virtual environment
        self.manager.create_virtualenv(self.test_env_name)
        
        # Test installing empty dependency list
        result = self.manager.install_dependencies(self.test_env_name, [])
        assert result is True
        
        # Test installing simple dependency
        # Note: Here we only test method call, not actual dependency installation, as it may be slow
        # If you need to test actual dependency installation, you can uncomment the following
        # result = self.manager.install_dependencies(self.test_env_name, ["requests"])
        # assert result is True
    
    def test_execute_in_venv(self):
        """Test execute script in virtual environment"""
        # Create virtual environment
        self.manager.create_virtualenv(self.test_env_name)
        
        # Create test script
        test_script = """import json
import sys

if len(sys.argv) > 1:
    params = json.loads(sys.argv[1])
    result = {"success": True, "result": params}
    print(json.dumps(result))
else:
    result = {"success": False, "error": "No parameters provided"}
    print(json.dumps(result))
"""
        
        # Write test script file
        script_path = os.path.join(self.temp_dir, "test_script.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(test_script)
        
        # Execute test script
        parameters = {"test": "value"}
        result = self.manager.execute_in_venv(self.test_env_name, script_path, parameters)
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_register_isolation_strategy(self):
        """Test register custom isolation strategy"""
        # Create test strategy class
        class TestStrategy:
            def execute(self, skill_name, parameters):
                return {"success": True, "skill_name": skill_name, "parameters": parameters}
        
        # Register strategy
        strategy_name = "test_strategy"
        self.manager.register_isolation_strategy(strategy_name, TestStrategy())
        
        # Test execute strategy
        result = self.manager.execute_with_strategy(strategy_name, "test_skill", {"param": "value"})
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["skill_name"] == "test_skill"
        assert result["parameters"] == {"param": "value"}
        
        # Test non-existent strategy
        result_nonexistent = self.manager.execute_with_strategy("nonexistent_strategy", "test_skill", {})
        assert isinstance(result_nonexistent, dict)
        assert result_nonexistent["success"] is False
    
    def test_cleanup_venv(self):
        """Test cleanup virtual environment"""
        # Create virtual environment
        self.manager.create_virtualenv(self.test_env_name)
        env_path = os.path.join(self.temp_dir, self.test_env_name)
        assert os.path.exists(env_path)
        
        # Cleanup virtual environment
        self.manager.cleanup_venv(self.test_env_name)
        assert not os.path.exists(env_path)
    
    def test_list_venvs(self):
        """Test list all virtual environments"""
        # Initial state should be empty list
        venvs = self.manager.list_venvs()
        assert isinstance(venvs, list)
        assert len(venvs) == 0
        
        # Create virtual environment
        self.manager.create_virtualenv(self.test_env_name)
        
        # List again, should contain the created virtual environment
        venvs = self.manager.list_venvs()
        assert isinstance(venvs, list)
        assert self.test_env_name in venvs


if __name__ == "__main__":
    pytest.main([__file__])
