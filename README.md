# Compiler-Compiler (编译器生成器)

一个基于Python实现的编译器生成器，能够根据输入的文法规则自动生成完整的编译器前端（词法分析器 + 语法分析器 + 中间代码生成器）。

## 📋 项目简介

本项目实现了一个完整的**Compiler-Compiler**系统，主要功能包括：

### 核心功能

1. **词法分析器自动生成**
   - 输入：正则表达式定义的词法规则
   - 输出：DFA（确定有限自动机）词法分析器
   - 技术：Thompson构造 → NFA → 子集构造 → DFA → 最小化

2. **语法分析器自动生成**
   - 输入：上下文无关文法（CFG）
   - 输出：LALR(1)语法分析器
   - 技术：LR(1)项目集构造 → LALR压缩 → 分析表生成

3. **中间代码生成**
   - 支持类型系统（int/bool）
   - 支持控制流（if/else、while）
   - 生成三地址码（Three-Address Code）
   - 采用回填技术处理跳转

### 特点

- ✅ **真正的自动生成**：不依赖手写的分析表
- ✅ **多文法支持**：可处理任意上下文无关文法
- ✅ **完整的编译器前端**：从词法分析到中间代码生成
- ✅ **工程化设计**：模块化、可扩展、易维护

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 无需额外依赖库（仅使用标准库）

### 基本使用

#### 方式1：分步骤演示（推荐）

```bash
# 阶段1：输入文法 → 自动生成编译器
# 阶段2：输入源程序 → 输出分析结果
python demo_two_stages.py <文法配置文件> <源程序文件>

# 示例
python demo_two_stages.py configs/grammar1_arithmetic.json test_programs/arithmetic_1.txt
```

#### 方式2：一步完成

```bash
python test_from_file.py <文法配置文件> <源程序文件>
```

### 测试中间代码生成

```bash
python tests/intermediate_code/test_ic_generation.py <源程序文件>
```

## 📊 项目结构

```
Compiler-Compiler-Construction/
├── lexical/              # 词法分析模块
│   ├── regex_parser.py   # 正则表达式解析
│   ├── nfa.py            # NFA构造（Thompson构造）
│   ├── dfa.py            # DFA构造（子集构造 + 最小化）
│   └── scanner.py        # 词法分析器
├── syntax/               # 语法分析模块
│   ├── grammar.py        # 文法定义
│   ├── lr1_builder.py    # LR(1)项目集构造
│   ├── lalr_builder.py   # LALR(1)压缩
│   └── generator.py      # 分析表生成
├── driver/               # 分析驱动器
│   ├── lr_parser.py      # LR分析器
│   └── semantic.py       # 语义分析和中间代码生成
├── configs/              # 文法配置文件
│   ├── grammar1_arithmetic.json      # 算术表达式文法
│   ├── grammar2_assignment.json      # 赋值语句文法
│   └── grammar_imperative.json       # 命令式语言文法
├── test_programs/        # 测试源程序
│   ├── arithmetic_1.txt              # 合法程序
│   ├── arithmetic_error1.txt         # 错误程序（负例测试）
│   └── intermediate_code/            # 中间代码测试
└── tests/                # 测试脚本
    ├── test_lex_syn.py               # 词法语法测试
    └── intermediate_code/            # 中间代码测试
```

## 📚 文档

- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - 技术实现详解（算法原理、数据结构）
- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - 演示指南（课程项目展示）
- **[DEMO_CHEAT_SHEET.md](DEMO_CHEAT_SHEET.md)** - 演示备忘单（快速参考）
- **[ERROR_TEST_README.md](ERROR_TEST_README.md)** - 错误测试说明

## 🎯 演示示例

### 示例1：算术表达式文法

**输入文法**（configs/grammar1_arithmetic.json）：
```
S -> E
E -> E + T | E - T | T
T -> T * F | T / F | F
F -> ( E ) | id | num
```

**自动生成**：
- 词法规则：8个
- DFA状态：9个
- LALR(1)状态：18个

**测试源程序**：`id + id * id`

**输出结果**：
- 合法性判断：✅ 合法语句
- 产生式序列：9步
- 语法树：JSON格式

### 示例2：中间代码生成

**输入源程序**：
```c
int x ;
int y ;
x := 10 ;
y := 20 ;
if ( x < y ) then x := x + 1 ;
```

**生成的三地址码**：
```
1: x := 10
2: y := 20
3: t1 := x < y
4: if_false t1 goto L1
5: t2 := x + 1
6: x := t2
7: L1:
```

## ✅ 测试覆盖

### 第一部分：词法和语法分析
- ✅ 2个不同文法（算术表达式、赋值语句）
- ✅ 每个文法 × 2个合法程序 = 4个正例测试（全部通过）
- ✅ 错误程序测试 = 2个负例测试（正确拒绝）
- ✅ 通过率：100%

### 第二部分：中间代码生成
- ✅ 1个命令式语言文法
- ✅ 4个测试程序（算术运算、if/else、while、布尔表达式）
- ✅ 通过率：100%

## 🔧 技术亮点

1. **Thompson构造法** - 将正则表达式转换为NFA
2. **子集构造法** - 将NFA确定化为DFA
3. **DFA最小化** - 等价状态分割法（Hopcroft算法）
4. **LALR(1)构造** - LR(1)项目集构造 + 同心集合并
5. **回填技术** - 控制流跳转的延迟绑定

详细技术实现请参考 [IMPLEMENTATION.md](IMPLEMENTATION.md)

## 🎓 课程要求完成情况

### A要求：自动生成
- ✅ 对不同的文法，能自动生成词法分析器和语法分析器
- ✅ 测试了2个不同文法（词法规则数、DFA状态数、LALR状态数都不同）
- ✅ 证明了真正的自动生成能力

### B要求：正确性测试
- ✅ 对生成的分析器，输入不同的源程序
- ✅ 正例测试：合法程序被正确接受
- ✅ 负例测试：非法程序被正确拒绝
- ✅ 全面验证了分析器的正确性

## 👥 开发团队

- **2354274 叶贤伟** - 词法/语法分析器自动生成
- **2353408 周由** - 语义分析和中间代码生成

---

**项目状态**：✅ 完成  
**最后更新**：2025年12月
