#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code quality check module
Responsible for checking the quality of skill code, including code style, complexity, potential errors, and security
"""

import os
import ast
import re
import sys
from typing import Dict, List, Any, Tuple


class CodeQualityChecker:
    """
    Code quality checker
    Provides code quality checking functionality
    """
    
    def __init__(self):
        """
        Initialize code quality checker
        """
        self.checks = {
            "code_style": self._check_code_style,
            "complexity": self._check_complexity,
            "potential_errors": self._check_potential_errors,
            "security": self._check_security
        }
    
    def check_code_quality(self, code: str, skill_name: str = "") -> Dict[str, Any]:
        """
        Check code quality
        
        Args:
            code: Code to check
            skill_name: Skill name (optional)
            
        Returns:
            Dict[str, Any]: Code quality check result, including issues for reflection mechanism
        """
        results = {
            "skill_name": skill_name,
            "has_issues": False,
            "issues": [],
            "improvement_suggestions": [],
            "quality_feedback": ""
        }
        
        # Execute various checks
        all_issues = []
        for check_name, check_func in self.checks.items():
            try:
                check_result = check_func(code)
                
                # Collect issues
                if "issues" in check_result:
                    all_issues.extend(check_result["issues"])
                if "suggestions" in check_result:
                    results["improvement_suggestions"].extend(check_result["suggestions"])
            except Exception as e:
                pass  # Ignore errors during checking
        
        # Organize issues
        if all_issues:
            results["has_issues"] = True
            results["issues"] = all_issues
            
            # Generate quality feedback for reflection mechanism
            feedback_parts = []
            feedback_parts.append("Code quality check found the following issues that need to be fixed:")
            
            for i, issue in enumerate(all_issues, 1):
                line_info = f"(Line {issue.get('line', 'N/A')})" if 'line' in issue else ""
                severity = issue.get('severity', 'info').upper()
                message = issue.get('message', 'No description')
                feedback_parts.append(f"{i}. [{severity}]{line_info} {message}")
            
            if results["improvement_suggestions"]:
                feedback_parts.append("\nImprovement suggestions:")
                for i, suggestion in enumerate(results["improvement_suggestions"], 1):
                    line_info = f"(Line {suggestion.get('line', 'N/A')})" if 'line' in suggestion else ""
                    message = suggestion.get('message', 'No description')
                    feedback_parts.append(f"{i}.{line_info} {message}")
            
            results["quality_feedback"] = "\n".join(feedback_parts)
        else:
            results["quality_feedback"] = "Code quality check found no serious issues."
        
        return results
    
    def _check_code_style(self, code: str) -> Dict[str, Any]:
        """
        Check code style
        
        Args:
            code: Code to check
            
        Returns:
            Dict[str, Any]: Code style check result
        """
        issues = []
        suggestions = []
        
        # Check indentation
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check if indentation is 4 spaces
            if line.startswith('    '):
                pass  # Correct indentation
            elif line.startswith(' '):
                # Check if it's other number of spaces
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces % 4 != 0:
                    issues.append({
                        "line": i,
                        "type": "code_style",
                        "severity": "warning",
                        "message": f"Indentation should be multiples of 4 spaces, currently {leading_spaces} spaces"
                    })
            elif line.startswith('\t'):
                issues.append({
                    "line": i,
                    "type": "code_style",
                    "severity": "warning",
                    "message": "Should use spaces instead of tabs for indentation"
                })
        
        # Check line length
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                issues.append({
                    "line": i,
                    "type": "code_style",
                    "severity": "warning",
                    "message": f"Line length exceeds 79 characters, currently {len(line)} characters"
                })
        
        # Check empty lines
        empty_lines = 0
        for i, line in enumerate(lines, 1):
            if not line.strip():
                empty_lines += 1
            else:
                if empty_lines > 2:
                    issues.append({
                        "line": i,
                        "type": "code_style",
                        "severity": "info",
                        "message": f"Consecutive empty lines should not exceed 2, currently {empty_lines}"
                    })
                empty_lines = 0
        
        # Check import statements
        import_lines = [line for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')]
        if len(import_lines) > 10:
            suggestions.append({
                "type": "code_style",
                "message": "Many import statements, consider modularizing related functionality"
            })
        
        return {
            "success": True,
            "score": max(0, 100 - len(issues) * 5),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _check_complexity(self, code: str) -> Dict[str, Any]:
        """
        Check code complexity
        
        Args:
            code: Code to check
            
        Returns:
            Dict[str, Any]: Code complexity check result
        """
        issues = []
        suggestions = []
        
        try:
            # Parse code
            tree = ast.parse(code)
            
            # Check function complexity
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_function_complexity(node)
                    if complexity > 10:
                        issues.append({
                            "line": node.lineno,
                            "type": "complexity",
                            "severity": "warning",
                            "message": f"Function {node.name} has high complexity ({complexity}), consider splitting"
                        })
                    elif complexity > 5:
                        suggestions.append({
                            "type": "complexity",
                            "message": f"Function {node.name} has complexity {complexity}, consider optimization"
                        })
            
            # Check code lines
            lines = code.split('\n')
            code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            if len(code_lines) > 100:
                issues.append({
                    "line": 1,
                    "type": "complexity",
                    "severity": "info",
                    "message": f"Many code lines ({len(code_lines)}), consider splitting functionality"
                })
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
        return {
            "success": True,
            "score": max(0, 100 - len(issues) * 10),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _calculate_function_complexity(self, node: ast.AST) -> int:
        """
        Calculate function complexity
        
        Args:
            node: Function node
            
        Returns:
            int: Function complexity
        """
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (
                ast.If, ast.For, ast.While, ast.Try,
                ast.And, ast.Or, ast.Break, ast.Continue
            )):
                complexity += 1
        
        return complexity
    
    def _check_potential_errors(self, code: str) -> Dict[str, Any]:
        """
        Check potential errors
        
        Args:
            code: Code to check
            
        Returns:
            Dict[str, Any]: Potential error check result
        """
        issues = []
        suggestions = []
        
        try:
            # Parse code
            tree = ast.parse(code)
            
            # Check unused variables
            used_vars = set()
            defined_vars = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Load):
                        used_vars.add(node.id)
                    elif isinstance(node.ctx, ast.Store):
                        defined_vars.add(node.id)
            
            unused_vars = defined_vars - used_vars
            if unused_vars:
                for var in unused_vars:
                    suggestions.append({
                        "type": "potential_error",
                        "message": f"Variable {var} is defined but not used"
                    })
            
            # Check exception handling
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    if not node.handlers:
                        issues.append({
                            "line": node.lineno,
                            "type": "potential_error",
                            "severity": "warning",
                            "message": "try block has no exception handlers"
                        })
                    for handler in node.handlers:
                        if isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
                            suggestions.append({
                                "line": handler.lineno,
                                "type": "potential_error",
                                "message": "Caught generic exception, suggest catching more specific exception types"
                            })
            
            # Check return values
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    has_return = False
                    for child in ast.walk(node):
                        if isinstance(child, ast.Return):
                            has_return = True
                            break
                    if not has_return:
                        suggestions.append({
                            "line": node.lineno,
                            "type": "potential_error",
                            "message": f"Function {node.name} may have no return value"
                        })
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
        return {
            "success": True,
            "score": max(0, 100 - len(issues) * 15),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _check_security(self, code: str) -> Dict[str, Any]:
        """
        Check code security
        
        Args:
            code: Code to check
            
        Returns:
            Dict[str, Any]: Security check result
        """
        issues = []
        suggestions = []
        
        # Check dangerous imports
        dangerous_imports = [
            "os", "subprocess", "sys", "eval", "exec",
            "pickle", "marshal", "ctypes", "shutil"
        ]
        
        for imp in dangerous_imports:
            if f"import {imp}" in code or f"from {imp} import" in code:
                issues.append({
                    "type": "security",
                    "severity": "warning",
                    "message": f"Used potentially dangerous module: {imp}"
                })
        
        # Check dangerous function calls
        dangerous_functions = [
            "eval(", "exec(", "compile(", "open(",
            "input(", "raw_input(", "subprocess.Popen(",
            "os.system(", "os.popen(", "os.spawnl("
        ]
        
        for func in dangerous_functions:
            if func in code:
                issues.append({
                    "type": "security",
                    "severity": "warning",
                    "message": f"Used potentially dangerous function: {func[:-1]}"
                })
        
        # Check hardcoded sensitive information
        patterns = [
            (r"api[_\s]*key['\"\s]*[:=][^,}]+',", "API key"),
            (r"password['\"\s]*[:=][^,}]+',", "password"),
            (r"secret['\"\s]*[:=][^,}]+',", "secret"),
            (r"token['\"\s]*[:=][^,}]+',", "token")
        ]
        
        for pattern, info_type in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({
                    "type": "security",
                    "severity": "warning",
                    "message": f"Potentially hardcoded {info_type}"
                })
        
        return {
            "success": True,
            "score": max(0, 100 - len(issues) * 20),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _calculate_overall_score(self, results: Dict[str, Any]) -> int:
        """
        Calculate overall score
        
        Args:
            results: Check results
            
        Returns:
            int: Overall score
        """
        scores = []
        
        for check_name, check_result in results["checks"].items():
            if check_result.get("success", False) and "score" in check_result:
                scores.append(check_result["score"])
        
        if not scores:
            return 0
        
        return sum(scores) // len(scores)
    
    def generate_quality_report(self, results: Dict[str, Any], format: str = "text") -> str:
        """
        Generate code quality report
        
        Args:
            results: Code quality check results
            format: Report format (text or json)
            
        Returns:
            str: Code quality report
        """
        if format == "json":
            import json
            return json.dumps(results, indent=2, ensure_ascii=False)
        
        # Generate text report
        report = []
        report.append(f"=== Code Quality Check Report ===")
        report.append(f"Skill name: {results.get('skill_name', 'Unknown')}")
        report.append(f"Overall score: {results.get('overall_score', 0)}/100")
        report.append("")
        
        # Check details
        report.append("=== Check Details ===")
        for check_name, check_result in results.get('checks', {}).items():
            report.append(f"\n{check_name}:")
            if check_result.get('success', False):
                report.append(f"  Score: {check_result.get('score', 0)}/100")
            else:
                report.append(f"  Error: {check_result.get('error', 'Unknown error')}")
        
        # Issue list
        issues = results.get('issues', [])
        if issues:
            report.append("\n=== Issue List ===")
            for i, issue in enumerate(issues, 1):
                line_info = f" (Line {issue.get('line', 'N/A')})" if 'line' in issue else ""
                severity = issue.get('severity', 'info').upper()
                report.append(f"{i}. [{severity}]{line_info} {issue.get('message', 'No description')}")
        
        # Suggestion list
        suggestions = results.get('suggestions', [])
        if suggestions:
            report.append("\n=== Suggestion List ===")
            for i, suggestion in enumerate(suggestions, 1):
                line_info = f" (Line {suggestion.get('line', 'N/A')})" if 'line' in suggestion else ""
                report.append(f"{i}.{line_info} {suggestion.get('message', 'No description')}")
        
        return "\n".join(report)


# Global code quality checker instance
code_quality_checker = CodeQualityChecker()
