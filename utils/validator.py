import ast
import re
import os
import subprocess
from typing import Dict, List, Any

def validate_code_syntax(code: str) -> Dict[str, Any]:
    """Validate code syntax"""
    try:
        ast.parse(code)
        return {"valid": True, "errors": []}
    except SyntaxError as e:
        return {
            "valid": False,
            "errors": [f"SyntaxError: {e.msg} at line {e.lineno}"]
        }

def validate_code_security(code: str) -> Dict[str, Any]:
    """Validate code security"""
    security_issues = []
    
    # Check dangerous imports
    dangerous_imports = [
        "os", "subprocess", "sys", "eval", "exec", "open",
        "pickle", "marshal", "ctypes", "socket", "requests"
    ]
    
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        # Check imports
        if "import" in line or "from" in line:
            for dangerous in dangerous_imports:
                if dangerous in line:
                    security_issues.append(f"Line {i}: Potentially dangerous import: {dangerous}")
        
        # Check dangerous function calls
        if any(func in line for func in ["eval(", "exec(", "open(", "subprocess.", "os.system"]):
            security_issues.append(f"Line {i}: Potentially dangerous function call")
        
        # Check file operations
        if "open(" in line:
            security_issues.append(f"Line {i}: File operation detected")
    
    return {
        "secure": len(security_issues) == 0,
        "issues": security_issues
    }

def validate_dependencies(dependencies: List[str]) -> Dict[str, Any]:
    """Validate dependency security"""
    safe_dependencies = [
        "numpy", "pandas", "scikit-learn", "matplotlib", "seaborn",
        "tensorflow", "torch", "keras", "scipy", "statsmodels"
    ]
    
    unknown_dependencies = []
    for dep in dependencies:
        dep_name = dep.split('==')[0].split('>=')[0].strip()
        if dep_name not in safe_dependencies:
            unknown_dependencies.append(dep)
    
    return {
        "safe": len(unknown_dependencies) == 0,
        "unknown_dependencies": unknown_dependencies
    }

def validate_skill(skill_code: str, dependencies: List[str]) -> Dict[str, Any]:
    """Validate skill security and correctness"""
    results = {
        "syntax": validate_code_syntax(skill_code),
        "security": validate_code_security(skill_code),
        "dependencies": validate_dependencies(dependencies)
    }
    
    results["valid"] = (
        results["syntax"]["valid"] and
        results["security"]["secure"] and
        results["dependencies"]["safe"]
    )
    
    return results
