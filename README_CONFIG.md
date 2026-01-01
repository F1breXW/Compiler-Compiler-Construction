# 编译器-编译器项目说明

## 项目结构

本项目实现了一个完全**配置驱动**的编译器生成系统，遵循良好的软件设计模式。

### 核心特性

1. **配置驱动架构**：文法定义完全从JSON配置文件读取，无需修改代码
2. **自动生成能力**：根据配置自动生成词法分析器和语法分析器
3. **易于扩展**：新增文法只需添加配置文件
4. **完整测试**：每个文法包含多个测试用例自动验证

### 目录结构

```
Compiler-Compiler-Construction/
├── configs/                    # 文法配置目录（JSON格式）
│   ├── grammar1_arithmetic.json    # 算术表达式文法
│   ├── grammar2_assignment.json    # 赋值语句文法
│   └── grammar3_typed.json         # 类型声明文法
│
├── lexical/                    # 词法分析生成器
│   ├── generator.py                # 词法生成器主类
│   ├── thompson.py                 # Thompson构造法
│   ├── regex_parser.py             # 正则表达式解析器
│   ├── subset_construction.py      # 子集构造法
│   ├── minimization.py             # DFA最小化
│   └── scanner.py                  # 扫描器（运行时）
│
├── syntax/                     # 语法分析生成器
│   ├── generator.py                # 语法生成器主类
│   ├── grammar.py                  # 文法表示
│   ├── first_follow.py             # FIRST/FOLLOW集计算
│   ├── lr1_builder.py              # LR(1)项目集构建
│   ├── lalr_builder.py             # LALR(1)压缩
│   └── table_builder.py            # 分析表构建
│
├── driver/                     # LR分析驱动程序
│   ├── lr_parser.py                # LR分析器
│   └── semantic_analyzer.py        # 语义分析器
│
├── utils/                      # 工具模块
│   ├── config_loader.py            # 配置加载器（新增）
│   ├── visualizer.py               # 可视化工具
│   └── file_io.py                  # 文件I/O
│
├── main_new.py                 # 主程序（配置驱动版本）
├── generated/                  # 生成的分析器输出
└── visualizations/             # DFA/NFA可视化图表
```

## 配置文件格式

文法配置使用JSON格式，示例：

```json
{
  "name": "算术表达式文法",
  "description": "支持加减乘除和括号的算术表达式文法",
  "lexical_rules": [
    {
      "pattern": "\\+",
      "token": "+",
      "description": "加号运算符"
    },
    {
      "pattern": "id",
      "token": "id",
      "description": "标识符"
    }
  ],
  "grammar_rules": [
    "S -> E",
    "E -> E + T",
    "E -> T"
  ],
  "test_cases": [
    {
      "input": "a + b * c",
      "expected": "legal",
      "description": "测试运算符优先级"
    }
  ]
}
```

## 使用方法

### 运行演示

```bash
python main_new.py
```

程序会自动：
1. 加载 `configs/` 目录下的所有文法配置
2. 为每个文法生成词法和语法分析器
3. 运行测试用例并输出结果
4. 生成可视化图表和分析表

### 添加新文法

1. 在 `configs/` 目录创建新的JSON配置文件
2. 按照格式定义词法规则、语法规则和测试用例
3. 重新运行 `main_new.py` 即可

无需修改任何代码！

## 设计模式应用

1. **Facade模式**：`CompilerGenerator` 类封装词法和语法生成器的复杂性
2. **Strategy模式**：`RegexParser` 支持不同的正则表达式解析策略
3. **Factory模式**：`ThompsonConstructor` 作为NFA状态工厂
4. **单一职责原则**：`ConfigLoader` 专门负责配置加载，`ConfigValidator` 负责验证
5. **开闭原则**：对扩展开放（新增文法），对修改封闭（无需改代码）
6. **数据驱动**：所有文法定义外部化为配置文件

## 技术实现

### 词法分析器生成

- **输入**：正则表达式（支持 `|`, `*`, `+`, `[]`, `()` 等）
- **过程**：正则解析 → Thompson构造 → 子集构造 → DFA最小化
- **输出**：DFA转换表 + Scanner

### 语法分析器生成

- **输入**：BNF文法规则
- **过程**：FIRST/FOLLOW → LR(1)项目集 → LALR(1)压缩 → 分析表
- **输出**：ACTION表 + GOTO表 + LRParser

### 中间代码生成

- 在语法分析过程中通过语义动作生成三地址码
- 支持算术表达式、赋值语句等

## 验证与测试

项目包含3个不同的文法配置，每个文法包含3个测试用例：
- **文法1**：算术表达式（加减乘除、括号）
- **文法2**：赋值语句
- **文法3**：类型声明（支持位运算）

所有测试用例自动运行，验证：
1. 合法程序能正确分析
2. 非法程序能正确拒绝
3. 产生式序列输出正确
4. 中间代码生成正确

## 课程要求符合性

✅ **自动生成**：根据输入文法自动生成词法/语法分析器  
✅ **多文法测试**：测试了3个不同的文法  
✅ **多程序测试**：每个文法测试了3个程序（含合法/非法）  
✅ **输出完整**：输出合法性判断、产生式序列、中间代码  
✅ **配置驱动**：证明是真正的"自动生成"而非硬编码
