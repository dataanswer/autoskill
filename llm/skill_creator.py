try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

from llm.llm_config import llm_config
import yaml
import os
import subprocess
from typing import Optional, List, Dict, Any
from core.skill_generator import SkillGenerator
from llm.reflection_engine import ReflectionEngine, validate_code
from core.skill_persistence import SkillPersistence
from core.code_quality import code_quality_checker

def load_env():
    """从.env文件加载配置"""
    env_vars = {}
    env_file = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def install_dependencies(dependencies: List[str]) -> bool:
    """Install dependencies"""
    if not dependencies:
        return True
    
    print(f"Installing dependencies: {dependencies}")
    try:
        for dep in dependencies:
            if dep:
                subprocess.run(["pip", "install", dep], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e.stderr}")
        return False

class LLMSkillCreator:
    def __init__(self, api_key: str = None, plugins_dir: str = None):
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI库未安装。请安装langchain依赖：\n"
                "pip install autoskill-ai[langchain]"
            )
        
        # 使用统一的配置
        self.api_key = api_key or llm_config.api_key
        self.model_name = llm_config.model
        self.base_url = llm_config.base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 如果未提供plugins_dir，则使用默认路径（AutoSkill内部）
        if plugins_dir is None:
            import os
            plugin_dir = os.path.dirname(os.path.dirname(__file__))
            plugins_dir = os.path.join(plugin_dir, "skills", "plugins")
        
        self.generator = SkillGenerator(plugins_dir)
        self.reflection_engine = ReflectionEngine(self.api_key)
        self.skill_persistence = SkillPersistence(plugins_dir)
    
    def create_skill(self, skill_name: str, task_description: str) -> str:
        print(f"开始生成技能: {skill_name}")
        
        # 第一步：生成初始代码
        prompt = f"""
        请根据以下任务描述生成一个完整的skill插件，包含：
        1. 核心逻辑代码（skill.py）
        2. 元数据（manifest.yaml）
        3. 依赖库（requirements.txt）
        
        任务描述：{task_description}
        
        要求：
        1. 核心逻辑必须包含execute函数，接收parameters参数并返回结果
        2. 结果格式必须是{{"success": bool, "result": any}}
        3. 元数据必须包含name、version、description、parameters等字段
        4. 依赖库必须包含所有需要的Python包
        5. 代码语法要求：
           - 使用兼容的Python 3.8+语法
           - 避免使用list[int]等类型注解，使用list代替
           - 不要使用Markdown代码块标记（如```python）
           - 注意算法参数限制，如make_blobs不支持noise参数
        6. 算法参数限制：
           - make_blobs: 支持n_samples, centers, cluster_std, random_state
           - make_classification: 支持n_samples, n_features, n_informative, n_redundant, random_state
           - 不要在不支持的函数中使用noise参数
        7. 数据生成：
           - 使用简单的生成数据，不要下载真实数据集
           - 控制数据规模，确保快速执行
        
        请分别输出：
        - CODE: 核心逻辑代码（纯Python代码，无Markdown标记）
        - MANIFEST: 元数据内容
        - DEPENDENCIES: 依赖库列表（每行一个）
        """
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.choices[0].message.content
        
        code = self._extract_section(content, "CODE")
        manifest_content = self._extract_section(content, "MANIFEST")
        dependencies_str = self._extract_section(content, "DEPENDENCIES")
        
        # 移除 Markdown 代码块标记
        dependencies_str = dependencies_str.replace("```", "").strip()
        manifest_content = manifest_content.replace("```", "").replace("yaml", "").replace("json", "").strip()
        
        dependencies = [dep.strip() for dep in dependencies_str.split("\n") if dep.strip()]
        
        # 第二步：验证代码
        print("验证代码...")
        validation_result = validate_code(code)
        if not validation_result["valid"]:
            print(f"代码验证失败: {validation_result['errors']}")
            # 使用反思机制修复语法错误
            print("使用反思机制修复语法错误...")
            error_msg = ", ".join(validation_result["errors"])
            code = self.reflection_engine.reflect_on_error(error_msg, code, task_description, skill_name=skill_name)
            print("修复完成")
        
        # 第三步：安装依赖
        install_dependencies(dependencies)
        
        # 第四步：解析manifest
        try:
            manifest = yaml.safe_load(manifest_content)
        except Exception as e:
            print(f"解析manifest失败: {e}")
            manifest = {
                "description": task_description,
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        
        # 第五步：生成技能
        skill_path = self.generator.generate_skill(
            skill_name=skill_name,
            description=manifest.get("description", task_description),
            code=code,
            parameters=manifest.get("parameters"),
            dependencies=dependencies
        )
        
        # 第六步：代码质量检查
        print("进行代码质量检查...")
        quality_result = code_quality_checker.check_code_quality(code, skill_name)
        
        # 如果发现质量问题，使用反思机制修复
        if quality_result.get("has_issues", False):
            print("发现代码质量问题，使用反思机制修复...")
            quality_feedback = quality_result.get("quality_feedback", "")
            
            # 使用反思机制修复代码质量问题
            fixed_code = self.reflection_engine.reflect_on_error(
                error_message=quality_feedback,
                code=code,
                task_description=task_description,
                skill_name=skill_name
            )
            
            # 更新代码
            code = fixed_code
            
            # 更新技能文件
            skill_module_path = os.path.join(skill_path, "skill.py")
            with open(skill_module_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            print("代码质量问题修复完成！")
        else:
            print("代码质量检查通过，未发现严重问题。")
        
        # 第七步：验证技能执行
        print("验证技能执行...")
        try:
            # 动态导入并执行
            import sys
            import importlib.util
            
            skill_module_path = os.path.join(skill_path, "skill.py")
            spec = importlib.util.spec_from_file_location("skill", skill_module_path)
            skill_module = importlib.util.module_from_spec(spec)
            sys.modules["skill"] = skill_module
            spec.loader.exec_module(skill_module)
            
            # 执行技能
            result = skill_module.execute({})
            print("技能执行验证成功！")
            return skill_path
            
        except Exception as e:
            print(f"技能执行验证失败: {e}")
            # 第七步：使用反思机制修复
            print("使用反思机制修复...")
            
            # 收集更多错误信息
            import traceback
            error_traceback = traceback.format_exc()
            error_msg = f"执行错误: {str(e)}\n\n错误堆栈:\n{error_traceback}\n\n请修复以下问题：\n1. 确保execute函数正确实现\n2. 确保返回格式为{{\"success\": bool, \"result\": any}}\n3. 处理所有可能的异常情况\n4. 验证所有依赖是否正确安装"
            
            fixed_code = self.reflection_engine.reflect_on_error(
                error_message=error_msg,
                code=code,
                task_description=task_description,
                skill_name=skill_name,
                file_path=skill_module_path
            )
            
            # 保存修复后的代码
            skill_module_path = os.path.join(skill_path, "skill.py")
            with open(skill_module_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)
            
            # 保存版本信息
            new_version = self.skill_persistence.update_skill_version(skill_name, f"修复错误: {str(e)[:100]}")
            print(f"已保存版本: {new_version}")
            
            # 再次验证
            try:
                spec = importlib.util.spec_from_file_location("skill", skill_module_path)
                skill_module = importlib.util.module_from_spec(spec)
                sys.modules["skill"] = skill_module
                spec.loader.exec_module(skill_module)
                result = skill_module.execute({})
                print("修复后技能执行验证成功！")
                return skill_path
            except Exception as e2:
                print(f"修复后仍然失败: {e2}")
                # 第八步：最多尝试3次
                max_attempts = 3
                for attempt in range(2, max_attempts + 1):
                    print(f"第 {attempt}/{max_attempts} 次尝试修复...")
                    
                    # 收集更多错误信息
                    error_traceback2 = traceback.format_exc()
                    error_msg2 = f"第{attempt}次执行错误: {str(e2)}\n\n错误堆栈:\n{error_traceback2}\n\n请修复以下问题：\n1. 确保execute函数正确实现\n2. 确保返回格式为{{\"success\": bool, \"result\": any}}\n3. 处理所有可能的异常情况\n4. 验证所有依赖是否正确安装"
                    
                    fixed_code2 = self.reflection_engine.reflect_on_error(
                        error_message=error_msg2,
                        code=fixed_code,
                        task_description=task_description,
                        skill_name=skill_name,
                        file_path=skill_module_path
                    )
                    
                    # 保存修复后的代码
                    with open(skill_module_path, "w", encoding="utf-8") as f:
                        f.write(fixed_code2)
                    
                    # 保存版本信息
                    new_version = self.skill_persistence.update_skill_version(skill_name, f"第{attempt}次修复错误: {str(e2)[:100]}")
                    print(f"已保存版本: {new_version}")
                    
                    # 验证
                    try:
                        spec = importlib.util.spec_from_file_location("skill", skill_module_path)
                        skill_module = importlib.util.module_from_spec(spec)
                        sys.modules["skill"] = skill_module
                        spec.loader.exec_module(skill_module)
                        result = skill_module.execute({})
                        print(f"第 {attempt} 次修复成功！")
                        return skill_path
                    except Exception as e3:
                        print(f"第 {attempt} 次修复仍然失败: {e3}")
                        e2 = e3
                        fixed_code = fixed_code2
                        continue
                
                print("达到最大尝试次数，返回生成的技能")
                return skill_path
    
    def _extract_section(self, content: str, section_name: str) -> str:
        start_marker = f"{section_name}:"
        end_markers = ["CODE:", "MANIFEST:", "DEPENDENCIES:"]
        end_markers.remove(start_marker)
        
        start_idx = content.find(start_marker)
        if start_idx == -1:
            return ""
        
        start_idx += len(start_marker)
        end_idx = len(content)
        
        for marker in end_markers:
            marker_idx = content.find(marker, start_idx)
            if marker_idx != -1 and marker_idx < end_idx:
                end_idx = marker_idx
        
        extracted = content[start_idx:end_idx].strip()
        
        # 移除Markdown代码块标记
        if section_name == "CODE":
            # 移除 ```python 和 ``` 标记
            if extracted.startswith("```python"):
                extracted = extracted[9:].strip()
            elif extracted.startswith("```"):
                extracted = extracted[3:].strip()
            
            if extracted.endswith("```"):
                extracted = extracted[:-3].strip()
            
            # 修复类型注解
            extracted = extracted.replace("list[int]", "list").replace("list[float]", "list").replace("list[str]", "list")
            extracted = extracted.replace("dict[str, any]", "dict").replace("dict[str, int]", "dict")
            
            # 移除不支持的参数
            extracted = extracted.replace("noise=0.1", "").replace("noise=0.2", "").replace("noise=0.05", "")
        
        return extracted
