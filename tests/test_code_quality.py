#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test code quality checking module
"""

import os
import sys
import pytest

# Add project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.code_quality import CodeQualityChecker, code_quality_checker


class TestCodeQualityChecker:
    """Test code quality checker"""
    
    def setup_method(self):
        """Set up test environment"""
        self.checker = CodeQualityChecker()
    
    def test_check_code_quality(self):
        """Test check code quality"""
        # Test simple code
        simple_code = """def add(a, b):
    return a + b
"""
        result = self.checker.check_code_quality(simple_code, "test_skill")
        assert isinstance(result, dict)
        assert result["skill_name"] == "test_skill"
        assert "has_issues" in result
        assert "issues" in result
        assert "improvement_suggestions" in result
        assert "quality_feedback" in result
    
    def test_check_code_style(self):
        """Test check code style"""
        # Test code with indentation issues
        bad_indent_code = """def add(a, b):
  return a + b
"""
        result = self.checker._check_code_style(bad_indent_code)
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "score" in result
        assert "issues" in result
        assert "suggestions" in result
    
    def test_check_complexity(self):
        """Test check code complexity"""
        # Test simple function
        simple_func = """def add(a, b):
    return a + b
"""
        result = self.checker._check_complexity(simple_func)
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "score" in result
        assert "issues" in result
        assert "suggestions" in result
        
        # Test complex function
        complex_func = """def complex_func(a, b, c):
    if a > b:
        if b > c:
            return a
        else:
            for i in range(10):
                if i > 5:
                    return c
                else:
                    continue
    elif a < b:
        while b > 0:
            b -= 1
        return b
    else:
        try:
            return a / c
        except Exception:
            return 0
"""
        result = self.checker._check_complexity(complex_func)
        assert isinstance(result, dict)
        assert result["success"] is True
    
    def test_check_potential_errors(self):
        """Test check potential errors"""
        # Test code with unused variable
        unused_var_code = """def add(a, b):
    c = 10
    return a + b
"""
        result = self.checker._check_potential_errors(unused_var_code)
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "score" in result
        assert "issues" in result
        assert "suggestions" in result
    
    def test_check_security(self):
        """Test check code security"""
        # Test code with dangerous function call
        dangerous_code = """def run_code(code):
    exec(code)
"""
        result = self.checker._check_security(dangerous_code)
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "score" in result
        assert "issues" in result
        assert "suggestions" in result
    
    def test_calculate_overall_score(self):
        """Test calculate overall score"""
        # Test calculate overall score
        results = {
            "checks": {
                "code_style": {"success": True, "score": 90},
                "complexity": {"success": True, "score": 80},
                "potential_errors": {"success": True, "score": 95},
                "security": {"success": True, "score": 85}
            }
        }
        score = self.checker._calculate_overall_score(results)
        assert isinstance(score, int)
        assert 0 <= score <= 100
    
    def test_generate_quality_report(self):
        """Test generate code quality report"""
        # Test generate text report
        results = {
            "skill_name": "test_skill",
            "overall_score": 85,
            "checks": {
                "code_style": {"success": True, "score": 90},
                "complexity": {"success": True, "score": 80},
                "potential_errors": {"success": True, "score": 95},
                "security": {"success": True, "score": 85}
            },
            "issues": [],
            "suggestions": []
        }
        text_report = self.checker.generate_quality_report(results, "text")
        assert isinstance(text_report, str)
        assert "Code Quality Check Report" in text_report
        
        # Test generate JSON report
        json_report = self.checker.generate_quality_report(results, "json")
        assert isinstance(json_report, str)
    
    def test_global_checker(self):
        """Test global code quality checker instance"""
        assert code_quality_checker is not None
        assert isinstance(code_quality_checker, CodeQualityChecker)


if __name__ == "__main__":
    pytest.main([__file__])
