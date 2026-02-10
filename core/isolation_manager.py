#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment isolation management module
Responsible for creating and managing isolated environments for skill execution
"""

import os
import sys
import subprocess
import venv
import shutil
from typing import Optional, Dict, Any, List


class IsolationManager:
    """
    Environment isolation manager
    Provides virtual environment creation, management, and execution functionality
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize environment isolation manager
        
        Args:
            base_dir: Base directory for storing virtual environments
        """
        self.base_dir = base_dir or os.path.join(os.path.dirname(__file__), "..", "venvs")
        os.makedirs(self.base_dir, exist_ok=True)
        self.isolation_configs = {}
    
    def create_virtualenv(self, env_name: str) -> str:
        """
        Create virtual environment
        
        Args:
            env_name: Virtual environment name
            
        Returns:
            str: Virtual environment path
        """
        env_path = os.path.join(self.base_dir, env_name)
        
        # If virtual environment already exists, return directly
        if os.path.exists(env_path):
            return env_path
        
        # Create virtual environment
        try:
            venv.create(env_path, with_pip=True)
            print(f"✓ Virtual environment created successfully: {env_path}")
            return env_path
        except Exception as e:
            print(f"✗ Failed to create virtual environment: {e}")
            raise
    
    def get_venv_python(self, env_name: str) -> Optional[str]:
        """
        Get Python executable path for virtual environment
        
        Args:
            env_name: Virtual environment name
            
        Returns:
            Optional[str]: Python executable path
        """
        env_path = os.path.join(self.base_dir, env_name)
        
        # Get Python executable path based on operating system
        if sys.platform == "win32":
            python_exe = os.path.join(env_path, "Scripts", "python.exe")
        else:
            python_exe = os.path.join(env_path, "bin", "python")
        
        if os.path.exists(python_exe):
            return python_exe
        return None
    
    def install_dependencies(self, env_name: str, dependencies: List[str]) -> bool:
        """
        Install dependencies in virtual environment
        
        Args:
            env_name: Virtual environment name
            dependencies: Dependency list
            
        Returns:
            bool: Whether installation was successful
        """
        if not dependencies:
            return True
        
        python_exe = self.get_venv_python(env_name)
        if not python_exe:
            print(f"✗ Virtual environment {env_name} does not exist")
            return False
        
        try:
            # Install pip
            subprocess.check_call([python_exe, "-m", "ensurepip", "--upgrade"])
            # Install dependencies
            for dep in dependencies:
                if dep and dep != "none":
                    subprocess.check_call([python_exe, "-m", "pip", "install", dep])
            print(f"✓ Dependencies installed successfully: {dependencies}")
            return True
        except Exception as e:
            print(f"✗ Failed to install dependencies: {e}")
            return False
    
    def execute_in_venv(self, env_name: str, script_path: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute script in virtual environment
        
        Args:
            env_name: Virtual environment name
            script_path: Script path
            parameters: Execution parameters
            
        Returns:
            Dict[str, Any]: Execution result
        """
        python_exe = self.get_venv_python(env_name)
        if not python_exe:
            return {"success": False, "error": f"Virtual environment {env_name} does not exist"}
        
        if not os.path.exists(script_path):
            return {"success": False, "error": f"Script path {script_path} does not exist"}
        
        try:
            # Build execution command
            import json
            params_json = json.dumps(parameters)
            cmd = [
                python_exe,
                script_path,
                params_json
            ]
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(script_path)
            )
            
            # Parse execution result
            if result.returncode == 0:
                try:
                    output = json.loads(result.stdout)
                    # Ensure return value is a dictionary
                    if not isinstance(output, dict):
                        # Special handling if it's the string "success"
                        if output == "success":
                            return {"success": True}
                        # Wrap other types as success result
                        return {"success": True, "result": output}
                    return output
                except json.JSONDecodeError:
                    # Even if parsing fails, check if output contains error information
                    if '{"success": False' in result.stdout or '{"success":false' in result.stdout:
                        return {"success": False, "error": result.stdout}
                    # Wrap other cases as success result
                    return {"success": True, "result": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def register_isolation_strategy(self, name: str, strategy: Any):
        """
        Register custom isolation strategy
        
        Args:
            name: Strategy name
            strategy: Strategy object, should implement execute method
        """
        self.isolation_configs[name] = strategy
    
    def execute_with_strategy(self, strategy_name: str, skill_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute skill with specified isolation strategy
        
        Args:
            strategy_name: Strategy name
            skill_name: Skill name
            parameters: Execution parameters
            
        Returns:
            Dict[str, Any]: Execution result
        """
        # Check if strategy exists
        if strategy_name not in self.isolation_configs:
            return {"success": False, "error": f"Isolation strategy {strategy_name} does not exist"}
        
        # Get strategy and execute
        strategy = self.isolation_configs[strategy_name]
        try:
            return strategy.execute(skill_name, parameters)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cleanup_venv(self, env_name: str):
        """
        Clean up virtual environment
        
        Args:
            env_name: Virtual environment name
        """
        env_path = os.path.join(self.base_dir, env_name)
        if os.path.exists(env_path):
            try:
                shutil.rmtree(env_path)
                print(f"✓ Virtual environment cleaned up successfully: {env_name}")
            except Exception as e:
                print(f"✗ Failed to clean up virtual environment: {e}")
    
    def list_venvs(self) -> List[str]:
        """
        List all virtual environments
        
        Returns:
            List[str]: Virtual environment list
        """
        if not os.path.exists(self.base_dir):
            return []
        
        venvs = []
        for item in os.listdir(self.base_dir):
            item_path = os.path.join(self.base_dir, item)
            if os.path.isdir(item_path):
                # Check if it's a virtual environment
                if sys.platform == "win32":
                    if os.path.exists(os.path.join(item_path, "Scripts", "python.exe")):
                        venvs.append(item)
                else:
                    if os.path.exists(os.path.join(item_path, "bin", "python")):
                        venvs.append(item)
        return venvs
