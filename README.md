# 编译器生成器 - PL/0语言编译器项目

## 项目简介

这是一个针对**PL/0语言**的编译器生成器，实现了从形式化规则自动生成词法分析表和语法分析表的完整功能。项目采用Python面向对象设计，包含详尽的中文注释，便于学习和扩展。

### 开发团队
- **2354274 叶贤伟** 核心算法引擎 - 词法/语法分析生成器
- **2353408 周由**: 语义分析逻辑 - 接入语义动作接口

---

## 功能模块

### 1. 词法分析生成器 (`lexical_generator.py`)

实现正则表达式到词法分析表的完整转换流程：

#### 核心算法
- **Thompson构造法** (RE → NFA)
  - 基本符号处理
  - 连接操作 (concatenation)
  - 选择操作 (alternation)
  - Kleene闭包 (star)

- **子集构造法** (NFA → DFA)
  - Epsilon闭包计算
  - Move操作
  - 状态子集映射

- **DFA最小化** (等价状态分割法)
  - Hopcroft算法
  - 状态等价类划分
  - 转换表压缩

#### 输出
- `transition_table`: 状态转换表 `{state: {symbol: next_state}}`
- `accepting_states`: 接受状态集合

#### 使用示例
```python
from lexical_generator import LexicalGenerator

generator = LexicalGenerator()
table, accepting = generator.generate("begin", "KEYWORD")
```

---

### 2. 语法分析生成器 (`parser_generator.py`)

实现LALR(1)分析表的自动构建：

#### 核心算法
- **FIRST集和FOLLOW集计算**
  - 终结符和非终结符的FIRST集
  - 非终结符的FOLLOW集
  - 符号串的FIRST集

- **LR(1)项目集规范族构建**
  - 项目闭包 (Closure)
  - GOTO函数
  - 状态转移图

- **LALR(1)压缩**
  - 同心项识别 (Core-identical items)
  - 向前看符号合并
  - 状态数量优化

- **分析表生成**
  - ACTION表 (shift/reduce/accept)
  - GOTO表
  - 冲突检测

#### 输入格式
```python
from parser_generator import Grammar

grammar = Grammar()
grammar.add_production("E", ["E", "+", "T"])
grammar.add_production("E", ["T"])
grammar.add_production("T", ["id"])
```

#### 输出
- `action_table`: `{(state, terminal): (action, value)}`
- `goto_table`: `{(state, non_terminal): next_state}`

---

### 3. LR分析驱动程序 (`parser_driver.py`)

基于栈的LR分析器，提供语义动作接口：

#### 主要功能
- **LR分析算法**
  - 状态栈和符号栈管理
  - Shift/Reduce操作
  - 错误检测和报告
  - 分析过程可视化

- **语义动作接口** (为同学B预留)
  ```python
  def semantic_handler(production, symbols):
      # production: 使用的产生式
      # symbols: 归约的符号列表
      # 返回: 综合属性值
      
      if production.left == "E" and len(symbols) == 3:
          # E -> E + T
          left = symbols[0].value
          right = symbols[2].value
          temp = new_temp()
          emit(f"{temp} = {left} + {right}")
          return temp
      
      return None
  ```

- **SemanticAnalyzer基类**
  - `new_temp()`: 生成临时变量
  - `emit(code)`: 生成三地址码
  - `add_symbol(name, type)`: 符号表操作
  - `lookup_symbol(name)`: 符号查询

#### 使用示例
```python
from parser_driver import LRParser, SemanticAnalyzer

analyzer = MySemanticAnalyzer()
parser = LRParser(grammar, action_table, goto_table,
                 semantic_handler=analyzer.semantic_action)
success = parser.parse(tokens)
```

---

## 项目结构

```
Compiler-Compiler-Construction/
│
├── lexical_generator.py    # 词法分析生成器
│   ├── State               # 状态类
│   ├── NFA                 # 非确定性有限自动机
│   ├── DFA                 # 确定性有限自动机
│   └── LexicalGenerator    # 主生成器类
│
├── parser_generator.py     # 语法分析生成器
│   ├── Production          # 产生式类
│   ├── LR1Item             # LR(1)项目
│   ├── Grammar             # 文法类
│   └── ParserGenerator     # 主生成器类
│
├── parser_driver.py        # LR分析驱动程序
│   ├── Symbol              # 符号类
│   ├── LRParser            # LR分析器
│   ├── SemanticAnalyzer    # 语义分析器基类
│   └── PL0SemanticAnalyzer # PL/0语义分析器示例
│
├── main.py                 # 主演示程序
└── README.md              # 项目文档 (本文件)
```

---

## 快速开始

### 运行完整演示
```bash
python main.py
```

这将执行以下演示：
1. 词法分析生成器演示 (3个示例)
2. 语法分析生成器演示 (完整LALR(1)构建)
3. LR分析驱动程序演示 (表达式解析)
4. 语义接口使用说明
5. 完整工作流程示例

### 测试单个模块

#### 词法分析器
```bash
python lexical_generator.py
```

#### 语法分析器
```bash
python parser_generator.py
```

#### 驱动程序
```bash
python parser_driver.py
```

---

## 给同学B的接口文档

### 步骤1: 创建自定义语义分析器

继承`SemanticAnalyzer`类：

```python
from parser_driver import SemanticAnalyzer, Symbol
from parser_generator import Production

class MySemanticAnalyzer(SemanticAnalyzer):
    def semantic_action(self, production: Production, symbols: List[Symbol]):
        """
        语义动作处理函数
        
        参数:
            production: 当前归约的产生式
            symbols: 归约的符号列表(从左到右)
        
        返回:
            该非终结符的综合属性值
        """
        # 根据产生式执行不同的语义动作
        if str(production) == "E -> E + T":
            # 处理加法
            left = symbols[0].value
            right = symbols[2].value
            temp = self.new_temp()
            self.emit(f"{temp} = {left} + {right}")
            return temp
        
        elif str(production) == "S -> id := E":
            # 处理赋值
            var = symbols[0].value
            expr = symbols[2].value
            self.emit(f"{var} = {expr}")
            return None
        
        # 默认: 传递第一个符号的值
        return symbols[0].value if symbols else None
```

### 步骤2: 集成到分析器

```python
from parser_driver import LRParser

# 创建语义分析器实例
analyzer = MySemanticAnalyzer()

# 创建LR分析器
parser = LRParser(
    grammar, 
    action_table, 
    goto_table,
    semantic_handler=analyzer.semantic_action  # 传入语义处理函数
)

# 执行分析
tokens = [('id', 'x'), (':=', ':='), ('num', 5)]
success = parser.parse(tokens)

# 获取结果
if success:
    code = analyzer.get_code()
    analyzer.print_intermediate_code()
    analyzer.print_symbol_table()
```

### 步骤3: 使用工具函数

```python
class MyAnalyzer(SemanticAnalyzer):
    def semantic_action(self, production, symbols):
        # 生成临时变量
        t1 = self.new_temp()  # 返回 "t1"
        t2 = self.new_temp()  # 返回 "t2"
        
        # 生成三地址码
        self.emit(f"{t1} = a + b")
        self.emit(f"{t2} = {t1} * c")
        
        # 符号表操作
        self.add_symbol("x", "integer")
        var_type = self.lookup_symbol("x")
        
        return t2
```

---

## 算法详解

### Thompson构造法 (RE → NFA)

**算法原理:**
1. **基本符号**: 对于字符a，创建 `start -a→ accept`
2. **连接**: 将第一个NFA的接受状态通过ε连接到第二个NFA的起始状态
3. **选择**: 创建新的起始和接受状态，用ε连接两个分支
4. **闭包**: 添加回边和跳过边

**时间复杂度**: O(n)，n为正则表达式长度

### 子集构造法 (NFA → DFA)

**算法原理:**
1. 初始状态 = ε-closure(NFA.start)
2. 对每个未处理的DFA状态和每个输入符号:
   - 计算 move(states, symbol)
   - 计算 ε-closure(move结果)
   - 如果是新状态，加入DFA
3. DFA状态包含NFA接受状态 → DFA接受状态

**时间复杂度**: O(2^n)，最坏情况，n为NFA状态数

### DFA最小化 (Hopcroft算法)

**算法原理:**
1. 初始划分: {接受状态, 非接受状态}
2. 迭代细化: 检查每组中的状态在相同输入下是否转移到同一分组
3. 如果不是，分裂该组
4. 重复直到不能再分裂

**时间复杂度**: O(n log n)，n为DFA状态数

### LR(1)项目集构建

**Closure算法:**
```
Closure(I):
  J = I
  repeat
    对于 [A → α·Bβ, a] ∈ J
      对于 B → γ
        对于 b ∈ FIRST(βa)
          将 [B → ·γ, b] 加入 J
  until J 不再变化
  return J
```

**GOTO算法:**
```
GOTO(I, X):
  J = { [A → αX·β, a] | [A → α·Xβ, a] ∈ I }
  return Closure(J)
```

**时间复杂度**: O(n³)，n为文法大小

### LALR(1)压缩

**算法原理:**
1. 提取每个LR(1)状态的核心(不含向前看符号)
2. 将具有相同核心的状态合并
3. 合并它们的向前看符号集合
4. 更新转移关系

**优势**: 状态数通常与LR(0)相同，远小于LR(1)

---

## 演示输出说明

### 词法分析器输出
```
[词法生成器] 开始处理正则表达式: begin
  [1/4] Thompson构造法: RE -> NFA
    NFA状态数: 6
  [2/4] 子集构造法: NFA -> DFA
    DFA状态数: 6
  [3/4] 等价状态分割: DFA最小化
    最小化DFA状态数: 6
  [4/4] 生成转换表
[词法生成器] 完成!
```

### 语法分析器输出
```
[语法生成器] 开始构建LALR(1)分析表
  [计算FIRST集]
    完成! 共计算15个符号的FIRST集
  [计算FOLLOW集]
    完成! 共计算5个非终结符的FOLLOW集
  [构建LR(1)项目集规范族]
    完成! LR(1)状态数: 42
  [合并LR(1)为LALR(1)]
    完成! LALR(1)状态数: 18 (从42个LR(1)状态压缩)
  [构建分析表]
    完成! ACTION表项: 35, GOTO表项: 12
```

### LR分析过程输出
```
步骤 1:
  状态栈: [0]
  符号栈: []
  当前状态: 0
  当前输入: id
  动作: SHIFT 5

步骤 2:
  状态栈: [0, 5]
  符号栈: ['id']
  当前状态: 5
  当前输入: +
  动作: REDUCE F -> id
    [语义动作] 产生式: F -> id
    [语义动作] 归约符号: ['id:a']
    [语义动作] 返回值: a
  GOTO 状态3
...
```

---

## 技术特点

### 1. 完全的面向对象设计
- 清晰的类层次结构
- 职责分离原则
- 易于扩展和维护

### 2. 详尽的中文注释
- 每个函数都有算法原理说明
- 关键步骤都有注释
- 便于学习和理解

### 3. 模块化设计
- 词法引擎和语法引擎完全解耦
- 可独立使用或组合使用
- 接口清晰明确

### 4. 防御性编程
- 输入验证
- 错误检测和报告
- 异常处理

### 5. 可扩展性
- 预留语义动作接口
- 支持自定义语义分析器
- 易于添加新功能

---

## 答辩演示建议

### 1. 词法分析演示 (3分钟)
- 展示正则表达式输入
- 显示Thompson构造的NFA
- 演示子集构造得到的DFA
- 展示最小化后的状态数对比

### 2. 语法分析演示 (5分钟)
- 展示BNF文法定义
- 显示FIRST和FOLLOW集
- 演示LR(1)到LALR(1)的压缩效果
- 展示生成的ACTION和GOTO表

### 3. 完整解析演示 (5分钟)
- 输入PL/0代码片段
- 逐步显示分析过程
- 展示状态栈和符号栈变化
- 显示生成的三地址码

### 4. 接口集成演示 (2分钟)
- 展示如何为同学B预留接口
- 演示语义动作钩子的使用
- 展示中间代码生成过程

---

## 依赖项

- Python 3.7+
- 标准库: `dataclasses`, `collections`, `typing`, `json`

无需安装第三方库！

---

## 许可证

本项目为教学项目，仅供学习使用。

---


## 致谢

感谢《编译原理》课程的理论基础，以及Aho、Ullman等前辈的经典教材《编译原理》(龙书)的指导。

---

**祝答辩顺利！** 🎉