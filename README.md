# AutoSkill

智能体自我进化插件，支持动态技能生成、执行和管理，可与LangChain无缝集成。通过LLM驱动的代码生成和执行，实现智能体的自我进化和能力扩展。

## 功能特性

- **动态技能生成**：基于LLM根据任务描述自动生成完整的技能代码
- **技能生命周期管理**：完整的技能注册、执行、版本控制和持久化机制
- **自我修复能力**：通过反思引擎分析执行错误并自动修复代码
- **技能模板系统**：内置多种技能模板，支持用户自定义和扩展
- **LangChain集成**：可与LangChain Agent无缝集成，增强智能体能力
- **安全措施**：代码验证、依赖审查、权限控制和执行环境隔离
- **配置系统**：支持默认配置、文件配置和环境变量
- **环境隔离**：支持多种执行环境隔离级别，确保安全性
- **技能指纹**：通过文本嵌入实现技能相似度检测，避免重复创建
- **代码质量检查**：自动检测和修复代码质量问题

## 目录结构

```
AutoSkill/
├── __init__.py          # 插件入口
├── core/                # 核心功能模块
│   ├── __init__.py
│   ├── plugin_manager.py     # 插件管理
│   ├── skill_registry.py     # 技能注册
│   ├── skill_executor.py     # 技能执行
│   ├── skill_generator.py    # 技能生成
│   ├── skill_persistence.py  # 技能持久化
│   ├── skill_fingerprint.py  # 技能指纹管理
│   ├── code_quality.py       # 代码质量检查
│   └── isolation_manager.py  # 环境隔离管理
├── llm/                 # LLM相关模块
│   ├── __init__.py
│   ├── skill_creator.py      # 技能创建
│   ├── reflection_engine.py  # 反思引擎
│   └── llm_config.py         # LLM配置
├── templates/           # 技能模板
│   ├── template_registry.py  # 模板注册
│   ├── base_skill.yaml       # 基础技能模板
│   ├── data_analysis.yaml    # 数据分析技能模板
│   └── machine_learning.yaml # 机器学习技能模板
├── config/              # 配置系统
│   ├── __init__.py
│   └── config.py             # 配置管理
├── integrations/        # 集成模块
│   ├── __init__.py
│   ├── toolkit.py            # 工具包
│   ├── tools.py              # 工具
│   ├── langchain_tool.py     # LangChain工具
│   └── langchain_example.py  # LangChain使用示例
├── examples/            # 使用示例
│   ├── basic_usage.py       # 基本使用示例
│   └── langchain_integration.py  # LangChain集成示例
├── utils/               # 工具函数
│   ├── validator.py          # 代码验证
│   └── dependency_manager.py # 依赖管理
├── skills/              # 技能插件目录
│   ├── fingerprints/         # 技能指纹存储
│   ├── skill_versions.json   # 技能版本信息
│   └── [技能名称]/            # 各技能目录
├── README.md            # 文档
├── CODE_QUALITY.md      # 代码质量文档
├── CONFIGURATION.md     # 配置文档
├── ISOLATION.md         # 环境隔离文档
├── requirements.txt     # 依赖文件
└── .env                 # 环境变量配置
```

## 系统要求

- **Python版本**: Python 3.11 或更高版本
- **操作系统**: Windows, macOS, Linux
- **内存**: 至少 4GB RAM
- **网络**: 需要网络连接以访问LLM API

## 安装方法

### 1. 从 PyPI 安装（推荐）

```bash
# 激活conda环境
conda activate mysite

# 从PyPI安装
pip install AutoSkill
```

### 2. 从本地安装（开发模式）

```bash
# 激活conda环境
conda activate mysite

# 克隆仓库
git clone https://github.com/auto-skill/AutoSkill.git
cd AutoSkill

# 安装依赖
pip install -r requirements.txt

# 以开发模式安装
pip install -e .
```

### 3. 配置环境变量

复制 `.env.example` 文件为 `.env`，并填入您的API密钥：

```bash
cp .env.example .env
# 编辑.env文件，填入API密钥
```

或者，您可以直接设置环境变量：

```bash
# 设置API密钥
export SKILL_AGENT_API_KEY="your-api-key"

# 设置其他环境变量（可选）
export SKILL_AGENT_MODEL="gpt-3.5-turbo"
export SKILL_AGENT_ISOLATION_LEVEL="none"
```

## 使用示例

### 基本使用

```python
from AutoSkill import AutoSkill

# 初始化AutoSkill
auto_skill = AutoSkill()

# 设置环境隔离级别（可选）
auto_skill.set_isolation_level("venv")

# 列出可用技能
skills = auto_skill.list_skills()
print(f"可用技能: {len(skills)} 个")

# 创建新技能
skill_path = auto_skill.create_skill(
    "hello_world",
    "创建一个简单的Hello World技能，接收name参数，返回问候语"
)
print(f"技能创建成功: {skill_path}")

# 执行技能
result = auto_skill.execute_skill("hello_world", {"name": "World"})
print(f"执行结果: {result}")

# 获取技能信息
skill_info = auto_skill.get_skill_info("hello_world")
print(f"技能信息: {skill_info}")

# 重新加载技能
auto_skill.reload_skills()

# 删除技能
auto_skill.delete_skill("hello_world")
```

### 使用技能模板

```python
# 使用数据分析模板创建技能
skill_path = auto_skill.create_skill(
    "data_analyzer",
    "创建一个数据分析技能，计算列表的平均值和标准差",
    template="data_analysis"
)

# 执行数据分析技能
result = auto_skill.execute_skill("data_analyzer", {"data": [1, 2, 3, 4, 5]})
print(f"数据分析结果: {result}")
```

### 与LangChain集成

#### 基本集成

```python
from langchain.llms import OpenAI
from AutoSkill.integrations import AutoSkillToolkit

# 初始化AutoSkill
auto_skill = AutoSkill()

# 创建LangChain工具包
toolkit = AutoSkillToolkit(auto_skill)
tools = toolkit.get_tools()

# 初始化LLM
llm = OpenAI(temperature=0.7)

# 创建智能体并执行任务
# 参考 integrations/langchain_example.py 中的示例代码
print("LangChain集成示例请参考 examples/langchain_integration.py 文件")
```

#### LangChain 集成示例演示

我们提供了两个 LangChain 集成示例：

1. **`examples/basic_usage.py`**：基础使用示例，展示 AutoSkill 的核心功能
2. **`examples/langchain_integration.py`**：LangChain 集成示例，展示如何将 AutoSkill 与 LangChain Agent 集成

##### `examples/basic_usage.py` 示例

**功能**：
- 初始化 AutoSkill
- 列出所有可用技能
- 创建新技能
- 执行技能
- 获取技能信息

**运行示例**：

在激活的 conda 环境中运行：

```bash
# 激活 conda 环境
conda activate mysite

# 运行示例脚本
python examples/basic_usage.py
```

**示例代码结构**：

```python
# 初始化 AutoSkill
auto_skill = AutoSkill(isolation_level="none")

# 列出所有可用技能
skills = auto_skill.list_skills()

# 创建新技能
skill_path = auto_skill.create_skill(skill_name, task_description)

# 执行技能
result = auto_skill.execute_skill("calculator", {"expression": "10 + 20"})

# 获取技能信息
skill_info = auto_skill.get_skill_info(skill_name)
```

##### `examples/langchain_integration.py` 示例

**功能**：
- 初始化 LLM 和 AutoSkill 工具
- 创建 LangChain Agent
- 执行现有技能（如计算器）
- 创建新技能（如天气查询）
- 展示 AutoSkill 与 LangChain 的无缝集成

**运行示例**：

在激活的 conda 环境中运行：

```bash
# 激活 conda 环境
conda activate mysite

# 运行演示脚本
python examples/langchain_integration.py
```

**示例代码结构**：

```python
# 初始化 LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 创建 AutoSkill 工具
auto_skill_tool = create_auto_skill_tool(isolation_level="none")

# 定义提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手，能够使用AutoSkill插件来创建和执行技能..."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 创建工具列表
tools = [auto_skill_tool]

# 创建Agent和Agent Executor
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 运行示例
response = agent_executor.invoke({
    "input": "使用计算器技能计算 100 + 200"
})
print(f"响应: {response['output']}")
```

**预期输出**：

```
====================================
AutoSkill 与 LangChain 集成示例
====================================

1. 初始化 LLM...
   ✓ LLM 初始化成功

2. 创建 AutoSkill 工具...
   ✓ AutoSkill 工具创建成功

3. 定义提示模板...
   ✓ 提示模板创建成功

4. 创建 Agent...
   ✓ Agent 创建成功

5. 创建 Agent Executor...
   ✓ Agent Executor 创建成功

6. 示例：使用计算器技能...
> Entering new AgentExecutor chain...

Invoking: `AutoSkill` with `{"action": "execute", "skill_name": "calculator", "parameters": {"expression": "100 + 200"}}`

{"success": true, "result": 300}

> Finished chain.
   ✓ Agent 响应: 计算结果为 300

7. 示例：创建新技能...
> Entering new AgentExecutor chain...

Invoking: `AutoSkill` with `{"action": "create", "skill_name": "weather_checker", "task_description": "创建一个天气查询技能，输入城市名称，返回该城市的当前天气"}`

技能创建成功，路径：D:\IDEProjects\AutoSkill\skills\weather_checker

> Finished chain.
   ✓ Agent 响应: 技能 `weather_checker` 已成功创建。你可以使用它来查询指定城市的当前天气。

====================================
集成示例演示完成！
====================================

💡 提示：
   - 确保已设置 AUTO_SKILL_API_KEY 环境变量
   - 可以通过 .env 文件或直接设置环境变量
   - 更多信息请参考 README.md
```

## 高级功能

### 动态工具管理

AutoSkill 支持动态工具管理，可以根据需要创建和管理技能。使用 `create_auto_skill_toolkit()` 可以创建一个工具包，它会自动管理所有可用的技能。

**示例代码**：

```python
from integrations.toolkit import create_auto_skill_toolkit

# 创建工具包
auto_skill_toolkit = create_auto_skill_toolkit(isolation_level="none")

# 获取所有工具
tools = auto_skill_toolkit.get_tools()

# 在 Agent 中使用
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

### 技能版本管理

**预期输出**：

```
====================================
AutoSkill 与 LangChain 集成示例演示
====================================

=== 示例1：列出所有可用技能 ===
可用技能数量: 9
- complex_data_analyzer: 执行 complex_data_analyzer 技能
- complex_machine_learning: 执行 complex_machine_learning 技能
- complex_nlp_processor: 执行 complex_nlp_processor 技能
- complex_time_series_analyzer: 执行 complex_time_series_analyzer 技能
- complex_web_crawler: 执行 complex_web_crawler 技能  
- data_processor_test: 执行 data_processor_test 技能  
- test_calculator: 执行 test_calculator 技能
- test_calculator_1769696108: 执行 test_calculator_1769696108 技能
- test_full_flow_1769696119: 执行 test_full_flow_1769696119 技能

=== 示例2：执行现有技能 ===

> Entering new AgentExecutor chain...

Invoking: `SkillAgent` with `{"action": "execute", "skill_name": "calculator", "parameters": {"expression": "100 + 200"}}`

{"success": false, "error": "技能 calculator 不存在"}
Invoking: `SkillAgent` with `{"action": "create", "skill_name": "calculator", "task_description": "创建一个 计算器技能，可以执行数学表达式计算"}`

技能创建成功，路径：D:\IDEProjects\MySite4.0.0\skill_agent_plugin1.0.0\skills\calculator
Invoking: `SkillAgent` with `{"action": "execute", "skill_name": "calculator", "parameters": {"expression": "100 + 200"}}`

{"success": true, "result": "执行 calculator 技能，参数：{'expression': '100 + 200'}"}计算结果为 300。     

> Finished chain.
响应: 计算结果为 300。

=== 示例3：创建新技能 ===

> Entering new AgentExecutor chain...

Invoking: `SkillAgent` with `{"action": "create", "skill_name": "weather_checker", "task_description": "创建一个天气查询技能，输入城市名称，返回该城市的当前天气"}`

技能创建成功，路径：D:\IDEProjects\MySite4.0.0\skill_agent_plugin1.0.0\skills\weather_checker技能 `weather_checker` 已成功创建。你可以使用它来查询指定城市的当前天气。需要我为你执行这个技能吗？如果是，请提供城市名称。

> Finished chain.
响应: 技能 `weather_checker` 已成功创建。你可以使用它 来查询指定城市的当前天气。需要我为你执行这个技能吗？如果是，请提供城市名称。

=== 示例4：动态管理技能 ===
初始技能列表:
技能数量: 11
技能名称: ['complex_data_analyzer', 'complex_machine_learning', 'complex_nlp_processor', 'complex_time_series_analyzer', 'complex_web_crawler', 'data_processor_test', 'test_calculator', 'test_calculator_1769696108', 'test_full_flow_1769696119', 'calculator', 'weather_checker']

创建新技能...
技能创建成功: D:\IDEProjects\MySite4.0.0\skill_agent_plugin1.0.0\skills\weather_checker

刷新技能列表...
刷新结果: 重新加载了 11 个技能
刷新后技能数量: 11
刷新后技能名称: ['calculator', 'complex_data_analyzer', 'complex_machine_learning', 'complex_nlp_processor', 'complex_time_series_analyzer', 'complex_web_crawler', 'data_processor_test', 'test_calculator', 'test_calculator_1769696108', 'test_full_flow_1769696119', 'weather_checker']

✓ 新技能已成功添加
  技能描述: 执行 weather_checker 技能

====================================
示例演示完成！
====================================
```

##### `complete_demo.py` 示例

**功能**：
- 完整的技能创建和执行流程演示
- 包括用户意图分析、技能规划、技能实现、技能执行、技能反思和技能优化等步骤
- 展示了基于 LLM 的真实技能反思和优化过程
- 不使用硬编码，完全基于自然语言指令

**运行示例**：

在激活的 conda 环境中运行：

```bash
# 激活 conda 环境
conda activate mysite

# 运行完整演示脚本
python integrations/complete_demo.py
```

**预期流程**：

1. **用户意图分析**：分析用户提出的销售数据分析需求
2. **技能规划**：系统规划如何实现销售数据分析技能
3. **技能实现**：自动创建销售数据分析技能
4. **技能执行**：执行技能分析销售数据
5. **技能反思**：系统反思技能执行结果，寻找优化空间
6. **技能优化**：优化技能，添加数据可视化和增长率计算功能
7. **技能再次执行**：使用优化后的技能再次执行任务

**示例说明**：

1. **完整流程**：演示了从用户意图到技能执行和反思优化的全过程
2. **真实反思**：展示了基于 LLM 的真实技能反思过程，不使用硬编码
3. **自然语言交互**：完全基于自然语言指令，模拟真实用户使用场景
4. **技能优化**：展示了如何通过反思优化技能功能

这个示例展示了 AutoSkill 的完整工作流程，从用户意图到技能执行和反思优化的全过程，体现了系统的智能性和灵活性。

##### 示例说明

1. **技能管理**：示例展示了如何列出、创建和执行技能
2. **自动技能创建**：当执行不存在的技能时，系统会自动创建该技能
3. **动态工具管理**：演示了如何刷新技能列表，使新创建的技能立即可用
4. **智能体交互**：展示了 LangChain Agent 如何与 AutoSkill 工具交互，处理用户请求
5. **技能反思**：展示了基于 LLM 的真实技能反思和优化过程

这些示例展示了 AutoSkill 与 LangChain 的无缝集成能力，使智能体能够通过自然语言指令创建和执行各种技能。

### 高级使用示例

#### 复杂数据分析技能

```python
# 创建复杂的数据分析技能
skill_path = skill_agent.create_skill(
    "complex_data_analyzer",
    "创建一个复杂的数据分析技能，能够：1. 读取CSV文件数据 2. 执行数据清洗（处理缺失值、异常值） 3. 生成多种统计分析（均值、中位数、标准差、相关性分析） 4. 创建数据可视化图表 5. 输出分析报告"
)

# 执行技能
result = skill_agent.execute_skill(
    "complex_data_analyzer",
    {"csv_data": "A,B,C\n1,2,3\n4,5,6\n7,8,9"}
)
print(f"分析结果: {result}")
```

#### 机器学习技能

```python
# 创建机器学习技能
skill_path = skill_agent.create_skill(
    "machine_learning_skill",
    "创建一个机器学习技能，支持分类和回归任务，自动执行数据预处理、模型训练和评估"
)

# 执行技能
result = skill_agent.execute_skill(
    "machine_learning_skill",
    {
        "data_type": "classification",
        "model_type": "random_forest",
        "n_samples": 100,
        "n_features": 4
    }
)
print(f"模型训练结果: {result}")
```

## 技能模板

内置模板：

- **base_skill**：基础技能模板，适用于通用技能创建
- **data_analysis**：数据分析技能模板，包含数据处理和统计分析功能
- **machine_learning**：机器学习技能模板，包含模型训练和评估功能

## 配置选项

### 配置文件

可以通过 `config.yaml` 文件配置插件，提供更详细的配置选项：

```yaml
# 插件基本配置
plugin:
  name: AutoSkill
  version: 1.0.0
  description: 智能体自我进化插件
  debug: false  # 是否启用调试模式

# LLM 配置
llm:
  provider: openai  # LLM 提供商，如 openai, anthropic, google 等
  api_key: "your-api-key"  # API 密钥
  base_url: "https://api.openai.com/v1"  # API 基础 URL
  model: gpt-4  # 使用的模型
  temperature: 0.7  # 生成温度
  max_tokens: 2000  # 最大生成 tokens
  timeout: 30  # 超时时间（秒）

# 技能配置
skills:
  plugins_dir: "skills/plugins"  # 技能插件目录
  auto_load: true  # 是否自动加载技能
  max_skills: 100  # 最大技能数量
  enable_fingerprints: true  # 是否启用技能指纹
  fingerprint_threshold: 0.8  # 技能相似度阈值

# 环境隔离配置
isolation:
  default_level: "none"  # 可选值: none, venv, custom
  venv_dir: "venvs"  # 虚拟环境目录
  venv_python_version: "3.11"  # 虚拟环境 Python 版本

# 模板配置
templates:
  dir: "templates"  # 模板目录
  default_template: "base_skill"  # 默认模板
  enable_custom_templates: true  # 是否启用自定义模板

# 安全配置
security:
  enable_code_validation: true  # 是否启用代码验证
  allow_external_dependencies: false  # 是否允许外部依赖
  max_execution_time: 60  # 最大执行时间（秒）
  max_memory_usage: 512  # 最大内存使用（MB）

# 性能配置
performance:
  enable_caching: true  # 是否启用缓存
  cache_dir: "cache"  # 缓存目录
  max_cache_size: 100  # 最大缓存大小
  cache_ttl: 3600  # 缓存过期时间（秒）

# 日志配置
logging:
  level: "info"  # 日志级别：debug, info, warning, error
  log_file: "auto_skill.log"  # 日志文件
  enable_console_logging: true  # 是否启用控制台日志
```

### 环境变量

以下是支持的环境变量及其默认值：

| 环境变量 | 描述 | 默认值 |
|---------|------|-------|
| `AUTO_SKILL_API_KEY` | LLM API密钥 | 无（必须设置） |
| `AUTO_SKILL_MODEL` | 使用的模型 | `gpt-3.5-turbo` |
| `AUTO_SKILL_BASE_URL` | API基础URL | 无（使用默认） |
| `AUTO_SKILL_ISOLATION_LEVEL` | 默认环境隔离级别 | `none` |
| `AUTO_SKILL_PLUGINS_DIR` | 技能插件目录 | `skills` |
| `AUTO_SKILL_CONFIG_FILE` | 配置文件路径 | 无（使用默认） |
| `AUTO_SKILL_DEBUG` | 是否启用调试模式 | `false` |
| `AUTO_SKILL_TEMPLATES_DIR` | 模板目录 | `templates` |
| `AUTO_SKILL_VENV_DIR` | 虚拟环境目录 | `venvs` |

### 配置优先级

配置优先级从高到低：
1. 环境变量
2. 配置文件 (`config.yaml`)
3. 默认配置

### 配置示例

#### 基本配置示例

```bash
# 设置 API 密钥
export AUTO_SKILL_API_KEY="your-api-key"

# 设置模型
export AUTO_SKILL_MODEL="gpt-4"

# 设置环境隔离级别
export AUTO_SKILL_ISOLATION_LEVEL="venv"
```

#### 高级配置示例

```yaml
# config.yaml
plugin:
  name: AutoSkill
  debug: true

llm:
  provider: openai
  api_key: "your-api-key"
  model: gpt-4-turbo
  temperature: 0.3

skills:
  plugins_dir: "my_skills"
  max_skills: 50

isolation:
  default_level: "venv"

security:
  enable_code_validation: true
  allow_external_dependencies: true
```

## 安全措施

1. **代码验证**：使用AST解析验证代码语法和安全性
2. **安全检查**：检测危险的导入和函数调用
3. **依赖审查**：验证依赖包的安全性和版本
4. **执行环境隔离**：支持多种隔离策略，限制技能执行环境
5. **权限控制**：控制技能的访问权限和执行权限
6. **输入验证**：验证技能输入参数的安全性

## 性能优化

1. **技能缓存**：缓存已加载的技能，提高执行速度
2. **延迟加载**：按需加载技能，减少启动时间
3. **并行执行**：支持并行执行技能，提高处理效率
4. **资源限制**：限制技能的内存和CPU使用，防止资源耗尽
5. **代码优化**：自动优化生成的代码，提高执行效率

## 环境隔离

AutoSkill支持多种环境隔离级别：

- **none**：无隔离，直接在当前环境执行（最快）
- **venv**：使用虚拟环境隔离，每个技能运行在独立的虚拟环境中
- **custom**：自定义隔离策略，可通过 `register_isolation_strategy` 注册

## 故障排除

### 常见问题

1. **API密钥错误**：确保在 `.env` 文件中正确配置了API密钥
2. **依赖安装失败**：确保网络连接正常，尝试使用代理
3. **技能执行失败**：检查技能代码是否有语法错误或逻辑错误
4. **LangChain集成失败**：确保已安装LangChain库
5. **环境隔离失败**：确保虚拟环境创建权限正确
6. **内存不足**：减少技能的复杂度或增加系统内存

### 日志

插件执行过程中的日志会输出到控制台，可根据日志信息排查问题。日志级别可通过配置文件调整。

### 调试技巧

1. **启用详细日志**：设置环境变量 `SKILL_AGENT_DEBUG=True`
2. **检查技能代码**：查看生成的技能代码，定位问题
3. **测试依赖**：单独测试技能依赖是否正确安装
4. **简化任务**：将复杂任务分解为简单任务，逐步测试

## 版本历史

- **v1.0.0**：初始版本
  - 实现动态技能生成
  - 支持技能生命周期管理
  - 集成LangChain
  - 实现安全措施

- **v1.1.0**：功能增强
  - 添加环境隔离功能
  - 实现技能指纹和相似度检测
  - 增强代码质量检查
  - 优化性能和安全性

## API 文档

### 核心 API

#### AutoSkill 类

**初始化**：
```python
from AutoSkill import AutoSkill

# 基本初始化
auto_skill = AutoSkill()

# 自定义配置初始化
auto_skill = AutoSkill(
    config={
        "skills": {
            "plugins_dir": "my_skills"
        },
        "isolation": {
            "default_level": "venv"
        }
    }
)
```

**主要方法**：

- `create_skill(skill_name, task_description, template=None)`: 创建新技能
- `execute_skill(skill_name, parameters)`: 执行技能
- `list_skills()`: 列出所有可用技能
- `get_skill_info(skill_name)`: 获取技能信息
- `update_skill(skill_name, improvements)`: 更新技能
- `delete_skill(skill_name)`: 删除技能
- `reload_skills()`: 重新加载技能
- `set_isolation_level(isolation_level)`: 设置环境隔离级别
- `get_isolation_level()`: 获取当前环境隔离级别

### 集成 API

#### LangChain 集成

```python
from integrations.langchain_tool import create_auto_skill_tool

# 创建技能代理工具
auto_skill_tool = create_auto_skill_tool(isolation_level="venv")

# 创建技能代理工具包
from integrations.toolkit import create_auto_skill_toolkit
auto_skill_toolkit = create_auto_skill_toolkit(isolation_level="venv")
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

### 贡献指南

1. **Fork仓库**：在GitHub上Fork项目仓库
2. **创建分支**：创建新的分支进行开发
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **安装开发依赖**：
   ```bash
   pip install -e "[dev]"
   ```
4. **编写代码**：遵循PEP 8代码风格，编写详细的文档和注释
5. **运行测试**：确保代码通过所有测试
   ```bash
   pytest
   ```
6. **运行代码质量检查**：
   ```bash
   black .
   isort .
   flake8
   ```
7. **提交更改**：提交代码更改并编写详细的提交信息
   ```bash
   git commit -m "Add: your feature description"
   ```
8. **创建Pull Request**：提交Pull Request，描述更改的内容和目的

### 开发规范

- **代码风格**：遵循PEP 8代码风格，使用black进行代码格式化
- **文档**：为所有公共方法和类编写详细的文档字符串
- **测试**：为新功能编写单元测试，确保测试覆盖率
- **提交信息**：使用清晰的提交信息格式，包括类型（Add, Fix, Update, Remove）和描述
- **分支管理**：使用feature分支进行开发，使用main分支进行发布

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/skill-agent/skill-agent-plugin.git
cd skill-agent-plugin

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装开发依赖
pip install -e "[dev]"

# 运行测试
pytest

# 运行代码质量检查
black .
isort .
flake8
```

## 联系方式

如有问题或建议，请通过以下方式联系我们：

- GitHub Issues：在项目仓库中创建Issue
- 电子邮件：dataanswer@163.com

## 致谢

感谢所有为项目做出贡献的开发者和用户！

---

**AutoSkill** - 让智能体自我进化，能力无限扩展！