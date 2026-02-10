import subprocess
import os
import sys
from typing import List, Dict, Any

def install_dependency(dependency: str) -> bool:
    """Install single dependency"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", dependency],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Successfully installed: {dependency}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {dependency}: {e.stderr}")
        return False

def install_dependencies(dependencies: List[str]) -> Dict[str, Any]:
    """Install multiple dependencies"""
    results = {
        "success": [],
        "failed": []
    }
    
    for dep in dependencies:
        if dep:
            if install_dependency(dep):
                results["success"].append(dep)
            else:
                results["failed"].append(dep)
    
    return results

def check_dependency(dependency: str) -> bool:
    """Check if dependency is installed"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", dependency.split('==')[0].split('>=')[0]],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def check_dependencies(dependencies: List[str]) -> Dict[str, Any]:
    """Check multiple dependencies"""
    results = {
        "installed": [],
        "missing": []
    }
    
    for dep in dependencies:
        if dep:
            dep_name = dep.split('==')[0].split('>=')[0]
            if check_dependency(dep_name):
                results["installed"].append(dep)
            else:
                results["missing"].append(dep)
    
    return results

def install_requirements_file(requirements_file: str) -> Dict[str, Any]:
    """Install dependencies from requirements.txt file"""
    if not os.path.exists(requirements_file):
        return {
            "success": [],
            "failed": [],
            "error": f"Requirements file not found: {requirements_file}"
        }
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Successfully installed dependencies from {requirements_file}")
        
        # Parse installation results
        with open(requirements_file, 'r') as f:
            dependencies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        return {
            "success": dependencies,
            "failed": []
        }
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e.stderr}")
        return {
            "success": [],
            "failed": [],
            "error": e.stderr
        }
