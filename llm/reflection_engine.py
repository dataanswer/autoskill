from .llm_config import llm_config
from openai import OpenAI
import ast
import re
from typing import Dict, List, Any, Optional

def validate_code(code: str) -> Dict[str, Any]:
    """Validate code syntax"""
    try:
        # Check syntax
        ast.parse(code)
        return {"valid": True, "errors": [], "code": code}
    except SyntaxError as e:
        # Only return syntax error message, no hardcoded fix
        errors = [f"SyntaxError: {e.msg} at line {e.lineno}"]
        return {"valid": False, "errors": errors, "code": code}

class ReflectionEngine:
    """Code reflection and repair engine"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or llm_config.api_key
        self.model_name = llm_config.model
        self.base_url = llm_config.base_url
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def reflect_on_error(self, error_message: str, code: str, task_description: str, skill_name: str = "", file_path: str = "") -> str:
        """Reflect on error and repair code"""
        # Extract error context information
        error_context = self._extract_error_context(code, error_message)
        
        prompt = f"""
        The following error occurred while executing the generated skill code:
        
        Skill name: {skill_name}
        File path: {file_path}
        Error message: {error_message}
        
        Error context: {error_context}
        
        Task description: {task_description}
        
        Current code:
        {code}
        
        Please analyze the error cause and provide the fixed code. Requirements:
        1. Keep the core functionality of the skill unchanged
        2. Only output the complete fixed code
        3. Do not use Markdown code block markers
        4. Ensure code syntax is correct
        5. Fix all parameter errors and syntax issues
        6. Keep the execute function interface unchanged
        7. Keep the original parameter names and functional semantics
        8. Use simple generated data, do not download real datasets
        9. Control data size to ensure fast execution
        10. Pay attention to checking the validity of function parameters, especially for data generation functions in scikit-learn
        """
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.choices[0].message.content
        return content.strip()
    
    def _extract_error_context(self, code: str, error_message: str) -> str:
        """Extract error context information"""
        # Analyze error message and extract key information
        context = []
        
        # Check if it's a parameter error
        if "unexpected keyword argument" in error_message:
            # Extract unsupported parameter name
            import re
            match = re.search(r"unexpected keyword argument '(.*)'", error_message)
            if match:
                param_name = match.group(1)
                context.append(f"Unsupported parameter: {param_name}")
                
                # Find where this parameter is used in the code
                lines = code.split('\n')
                for i, line in enumerate(lines, 1):
                    if f"{param_name}=" in line:
                        context.append(f"Parameter usage location: Line {i} - {line.strip()}")
        
        # Check if it's a syntax error
        elif "invalid syntax" in error_message:
            context.append("Syntax error, please check code syntax")
        
        # Check if it's an import error
        elif "No module named" in error_message:
            context.append("Import error, please check dependency libraries")
        
        # Add general context information
        context.append("Please check if function calls and parameter usage in the code are correct")
        context.append("Note: Some functions in scikit-learn may not support specific parameters")
        
        return "\n".join(context)
    
    def optimize_code(self, code: str, task_description: str) -> str:
        """Optimize code quality and performance"""
        prompt = f"""
        Please optimize the following skill code to improve its quality and performance:
        
        Task description: {task_description}
        
        Current code:
        {code}
        
        Optimization requirements:
        1. Keep the core functionality of the skill unchanged
        2. Keep the execute function interface unchanged
        3. Keep the original parameter names and functional semantics
        4. Improve code readability and maintainability
        5. Optimize performance, especially for data processing parts
        6. Add appropriate error handling
        7. Ensure parameter validation and default value settings
        8. Do not use Markdown code block markers
        9. Do not change the basic functional logic of the skill
        10. Only fix code quality issues, do not introduce new features
        """
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.choices[0].message.content
        return content.strip()
    
    def generate_fix(self, error_type: str, code: str, context: str) -> str:
        """Generate specific fix based on error type"""
        prompt = f"""
        The code encountered the following type of error: {error_type}
        
        Context information: {context}
        
        Current code:
        {code}
        
        Please generate the fixed code with the following requirements:
        1. Only output the complete fixed code
        2. Do not use Markdown code block markers
        3. Ensure code syntax is correct
        4. Keep the execute function interface unchanged
        """
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.choices[0].message.content
        return content.strip()
