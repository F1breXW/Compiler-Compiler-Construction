# 课程项目演示指南

**项目名称**: Compiler-Compiler (编译器生成器)  
**演示时间**: 建议25-30分钟  
**准备工作**: 确保所有测试程序和配置文件完整

---

## 📋 演示内容概览

### 第一部分：词法和语法分析（自动生成）- 15分钟
- ✅ 测试2个不同文法（满足≥2个要求）
- ✅ 每个文法测试2个程序（满足≥2个要求）
- ✅ 展示自动生成过程
- ✅ 展示合法性判断 + 产生式序列 + 语法树

### 第二部分：中间代码生成 - 10分钟
- ✅ 1个文法（命令式语言）
- ✅ 测试4个程序（超出≥2个要求）
- ✅ 展示三地址码生成
- ✅ 展示错误处理

---

## 🎬 详细演示流程

### 🌟 推荐演示方式：使用分步骤脚本

为了清晰展示**两个独立阶段**（符合课程要求），建议使用 `demo_two_stages.py`：

#### 演示命令格式
```bash
python demo_two_stages.py <文法配置文件> <源程序文件>
```

#### 优势
- ✅ **清晰分离两个阶段**：阶段1生成编译器 → 阶段2测试源程序
- ✅ **自动暂停**：阶段1完成后按回车继续，方便讲解
- ✅ **明确展示输出**：
  - 阶段1输出：词法规则数、DFA状态数、LALR状态数
  - 阶段2输出：合法性判断、产生式序列、语法树
- ✅ **符合要求描述**："输入文法 → 生成分析器" 和 "输入源程序 → 输出结果" 完全分开

#### 示例演示
```bash
# 文法1测试1
python demo_two_stages.py configs/grammar1_arithmetic.json test_programs/arithmetic_1.txt

# 文法1测试2
python demo_two_stages.py configs/grammar1_arithmetic.json test_programs/arithmetic_2.txt

# 文法2测试1（⭐ 强调文法差异）
python demo_two_stages.py configs/grammar2_assignment.json test_programs/assignment_1.txt

# 文法2测试2
python demo_two_stages.py configs/grammar2_assignment.json test_programs/assignment_2.txt
```

---

## 🎬 详细演示流程（使用分步骤脚本）

## 第一部分：词法和语法分析自动生成（15分钟）

### 🔹 演示1.1：算术表达式文法（5分钟）

#### 使用分步骤脚本
```bash
python demo_two_stages.py configs/grammar1_arithmetic.json test_programs/arithmetic_1.txt
```

**阶段1讲解要点**（编译器自动生成）：
1. **输入**：文法配置文件 `grammar1_arithmetic.json`
2. **自动生成词法分析器**：
   - 词法规则数：8个
   - DFA状态数：9个
   - Thompson构造 → NFA → DFA → 最小化
   - **可视化**：生成 `visualizations/算术表达式文法_dfa.dot`
3. **自动生成语法分析器**：
   - 文法产生式：10个
   - LALR(1)状态数：18个（从33个LR(1)状态压缩）
   - 完全自动构建分析表
   - **可视化**：生成 `visualizations/算术表达式文法_lalr_table.html`
4. **强调**：这些都是自动生成的，不是手写的！

**【可选：展示可视化结果】**
```bash
# 查看生成的DFA图（需要Graphviz支持，或直接展示文件存在）
ls visualizations/*.dot

# 查看生成的LALR分析表（推荐！）
start visualizations/算术表达式文法_lalr_table.html
```

**【按回车键暂停，讲解完毕后继续】**

**阶段2讲解要点**（测试源程序）：
1. **输入**：源程序 `id + id * id`
2. **输出1**：合法性判断 → 合法语句
3. **输出2**：产生式序列 → 9步归约
4. **输出3**：语法树 → JSON格式保存

#### 再测试第二个程序
```bash
python demo_two_stages.py configs/grammar1_arithmetic.json test_programs/arithmetic_2.txt
```

**源程序**：`( id + id ) * id`  
**讲解要点**：同一个文法，不同的源程序，产生式序列变为12步

---

### 🔹 演示1.2：赋值语句文法（5分钟）

#### 测试第一个程序（⭐ 重点展示文法差异）
```bash
python demo_two_stages.py configs/grammar2_assignment.json test_programs/assignment_1.txt
```

**阶段1讲解要点**（⭐⭐⭐ 核心要点 - 证明自动生成）：
1. **输入**：**完全不同的文法** `grammar2_assignment.json`
2. **观察自动生成的差异**：
   - 词法规则：从**8个变为5个**
   - DFA状态：从**9个变为7个**
   - LALR状态：从**18个变为12个**
   - 文法产生式：从10个变为4个
3. **强调**："可以看到，系统自动识别了文法的差异，重新生成了完全不同的分析器。如果是手写的分析表，不可能自动适应不同的文法！"

**【按回车键暂停，充分讲解文法差异】**

**阶段2讲解要点**：
1. **输入**：源程序 `x := id + id`
2. **输出**：合法性判断、产生式序列（5步）、语法树
3. **对比**：产生式序列比文法1更简洁（5步 vs 9步）

#### 再测试第二个程序
```bash
python demo_two_stages.py configs/grammar2_assignment.json test_programs/assignment_2.txt
```

**源程序**：`result := id - num`  
**讲解要点**：验证不同源程序的正确性

---

### � 演示1.3：错误检测能力（3分钟）⭐ 重要补充

#### 为什么需要测试错误程序？
**正确性测试（B要求）应该包括**：
- ✅ 能接受合法的程序（正例测试）
- ✅ 能拒绝非法的程序（负例测试）← 证明真正理解文法

#### 测试算术表达式的错误程序
```bash
# 错误1：连续运算符（id + * id）
python demo_two_stages.py configs/grammar1_arithmetic.json test_programs/arithmetic_error1.txt
```

**讲解要点**：
- **源程序**：`id + * id`（缺少操作数）
- **预期结果**：语法分析器检测到错误
- **实际输出**：❌ 非法语句（语法错误）
- **错误位置**：状态8无法处理输入'*'
- **说明**：正确识别了语法错误，不会误判为合法程序

#### 测试赋值语句的错误程序（可选）
```bash
# 错误2：使用=而不是:=
python demo_two_stages.py configs/grammar2_assignment.json test_programs/assignment_error1.txt
```

**讲解要点**：
- **源程序**：`x = id + id`（错误的赋值符号）
- **预期结果**：词法或语法错误
- **说明**：证明系统能识别不符合文法的程序

---

### �📊 第一部分总结（可选，如果时间充裕）

#### 自动生成能力对比表

演示完成后，可以展示这个对比表，证明系统真正实现了**自动生成**：

| 对比项 | 文法1（算术表达式） | 文法2（赋值语句） | 说明 |
|--------|---------------------|-------------------|------|
| **文法类型** | 算术表达式 | 赋值语句 | **完全不同的文法** |
| **词法规则数** | 8个 | 5个 | 自动适应文法需求 |
| **DFA状态数** | 9个 | 7个 | 自动构建不同的DFA |
| **LALR状态数** | 18个 | 12个 | 自动生成不同的分析表 |
| **测试程序1** | `id + id * id` | `x := id + id` | 不同语法结构 |
| **产生式步数** | 9步 | 5步 | 复杂度不同 |
| **测试程序2** | `( id + id ) * id` | `result := id - num` | 验证正确性 |
| **产生式步数** | 12步 | 5步 | 都能正确处理 |
| **错误测试** | `id + * id` | `x = id + id` | 正确拒绝 |
| **错误检测** | ❌ 语法错误 | ❌ 词法/语法错误 | 能识别错误 |

**关键结论**：
- ✅ **A要求：自动生成** - 证明了对不同文法能自动生成不同的分析器
- ✅ **B要求：正确性测试** - 每个文法测试2个正确程序+1个错误程序
  - 正确程序：能接受并正确分析
  - 错误程序：能拒绝并报告错误
  - **全面验证了分析器的正确性**

```bash
# 展示完整的测试报告
notepad TEST_REPORT.md
```

**统计数据**：
- ✅ 测试了**2个文法**（满足要求）
- ✅ 每个文法测试了**2个程序**（满足要求）
- ✅ 通过率：**100%**

---

## 第二部分：中间代码生成（10分钟）

### 🔹 演示2.1：展示文法配置（1分钟）

```bash
# 展示用于中间代码生成的文法
notepad configs/grammar_imperative.json
```

**讲解要点**：
- 这是一个**命令式语言文法**
- 支持类型声明（int/bool）
- 支持控制流（if/else、while）
- 支持布尔表达式和算术运算

---

### 🔹 演示2.2：基础测试 - 算术运算（2分钟）

```bash
python tests/intermediate_code/test_ic_generation.py configs/grammar_imperative.json test_programs/intermediate_code/ic_test1_arithmetic.txt
```

**源程序内容**：
```
int x ;
int y ;
int result ;
x := 10 ;
y := 20 ;
result := x + y * 2 ;
```

**演示要点**：
1. **语法分析**：显示完整的LR分析过程
2. **符号表**：展示类型检查
   ```
   x: int (已初始化)
   y: int (已初始化)
   result: int (已初始化)
   ```
3. **三地址码**：展示生成的5条指令
   ```
   1: x := 10
   2: y := 20
   3: t1 := y * 2
   4: t2 := x + t1
   5: result := t2
   ```
4. **保存文件**：打开 `generated/ic_test1_arithmetic_ir.txt`

---

### 🔹 演示2.3：错误处理（可选，1分钟）

创建一个错误的测试文件：
```bash
# 创建临时错误文件
echo "x := + ;" > test_error.txt

# 测试错误处理
python tests/intermediate_code/test_ic_generation.py configs/grammar_imperative.json test_error.txt
```

**演示要点**：
- 系统能检测语法错误
- 给出适当的错误报告

---

### 📊 第二部分总结（1分钟）

```bash
# 展示中间代码生成报告
notepad reports/IC_GENERATION_REPORT.md
```

**统计数据**：
- ✅ 完成了**1个文法**的中间代码生成（满足要求）
- ✅ 测试了**4个程序**（超出≥2个要求）
- ✅ 通过率：**100%**

---

## 🎯 快速演示模式（如果时间紧张，18分钟版本）

### 第一部分：词法和语法分析（10分钟）

```bash
# 文法1 - 算术表达式（正确程序，3分钟）
python demo_two_stages.py configs/grammar1_arithmetic.json test_programs/arithmetic_1.txt
python demo_two_stages.py configs/grammar1_arithmetic.json test_programs/arithmetic_2.txt

# 文法2 - 赋值语句（正确程序，强调差异，3分钟）
python demo_two_stages.py configs/grammar2_assignment.json test_programs/assignment_1.txt
python demo_two_stages.py configs/grammar2_assignment.json test_programs/assignment_2.txt

# 错误检测（验证正确性，2分钟）
python demo_two_stages.py configs/grammar1_arithmetic.json test_programs/arithmetic_error1.txt

# 对比总结（2分钟）
# 展示：2个文法自动生成，4个正确程序通过，1个错误程序被拒绝
```

### 第二部分：中间代码生成（7分钟）

```bash
# 算术运算（2分钟）
python tests/intermediate_code/test_ic_generation.py configs/grammar_imperative.json test_programs/intermediate_code/ic_test1_arithmetic.txt

# 错误处理（1分钟）
python tests/intermediate_code/test_ic_generation.py configs/grammar_imperative.json test_error.txt
```

### 总结（1分钟）

> "演示完成。第一部分测试了2个不同文法的自动生成，包括4个正确程序和1个错误程序，验证了自动生成能力和正确性。第二部分展示了中间代码生成。谢谢老师！"

---

## 🎯 推荐演示方式：手动运行

由于我们删除了旧的自动化脚本，建议直接使用以下命令进行演示：

### 方式1：手动逐个运行

如果需要手动控制，可以参考下面的命令清单。

---

## 📝 演示准备清单

### 提前准备（演示前30分钟）

- [ ] 测试演示脚本确保能正常运行
  ```bash
  python demo_two_stages.py configs/grammar1_arithmetic.json test_programs/arithmetic_1.txt
  ```
- [ ] 准备好所有要打开的文件路径
- [ ] 清空generated/目录（可选，让生成过程更明显）
- [ ] 调整终端字体大小（确保观众能看清）
- [ ] 准备计时器
- [ ] 准备备用方案（如果现场出问题，使用录屏）

### 终端准备

```bash
# 设置当前目录
cd 'E:\code\project\Compiler-Compiler Construction\Compiler-Compiler-Construction'

# 清空生成文件（可选）
Remove-Item generated/* -ErrorAction SilentlyContinue

# 测试Python环境
python --version
```

### 文件准备

提前在多个编辑器窗口中打开：
1. `configs/grammar1_arithmetic.json`
2. `configs/grammar2_assignment.json`
3. `configs/grammar_imperative.json`
4. `TEST_REPORT.md`
5. `reports/IC_GENERATION_REPORT.md`

---

## 🎤 演讲要点

### 开场白（1分钟）

> "各位老师好，我们的项目是一个**编译器生成器（Compiler-Compiler）**，能够根据输入的文法规则自动生成编译器。项目分为两部分：第一部分是词法和语法分析器的自动生成，第二部分是中间代码生成。"

### 第一部分介绍

> "首先演示第一部分：词法和语法分析的自动生成。我们实现了完整的自动生成流程，包括Thompson构造、子集构造、DFA最小化、以及LALR(1)分析表构建。
> 
> **关键是，我们将测试2个完全不同的文法**：算术表达式文法和赋值语句文法。系统会根据不同的文法配置，自动生成不同的词法分析器和语法分析器，包括不同数量的DFA状态和LALR状态。这证明了我们的编译器生成器的自动化能力。
> 
> **同时，对于正确性测试**，我们不仅测试合法的程序，还会测试非法的程序，验证分析器能正确识别错误。"

### 第二部分介绍

> "第二部分是中间代码生成。我们设计了一个命令式语言文法，支持类型检查和算术表达式。系统采用语法制导翻译技术，在语法分析的同时生成三地址码..."

### 结束语（1分钟）

> "以上就是我们的演示。项目实现了完整的编译器前端，从词法分析到中间代码生成。测试覆盖率100%，所有测试用例通过。谢谢老师！"

---

## 💡 常见问题准备

### Q1: 为什么选择LALR(1)而不是LL(1)？
**A**: LALR(1)能处理更广泛的文法，特别是左递归文法。我们的实现包括完整的LR(1)项目集构建和LALR压缩优化。

### Q3: 临时变量如何管理？
**A**: 系统维护一个临时变量计数器，自动生成t1、t2等临时变量名，确保不会重复。

### Q4: 如何扩展支持新的文法？
**A**: 只需编写JSON配置文件，定义词法规则和文法规则。系统会自动生成对应的编译器。

### Q5: 项目的创新点是什么？
**A**: 
1. 完整实现了编译器前端的所有阶段
2. 真正的自动化生成（不是手写分析表）
3. 支持高级特性（类型检查）
4. 工程化设计（模块化、可扩展）

---

## 🎬 演示脚本（逐字稿）

如果需要更详细的演讲稿，请查看 `DEMO_SCRIPT.md`

---

## 📹 备用方案

### 如果现场演示出问题

1. **使用录屏视频**：提前录制好演示视频
2. **展示测试报告**：直接打开TEST_REPORT.md和IC_GENERATION_REPORT.md
3. **展示代码**：打开核心算法代码进行讲解

### 录屏准备

建议提前录制：
- 完整演示视频（25分钟）
- 快速演示视频（15分钟）
- 各个模块的独立演示（3-5分钟/个）

---

## ✅ 最终检查清单

演示前最后检查：

- [ ] 所有Python依赖已安装
- [ ] 所有测试命令可以正常运行
- [ ] generated/目录已清空
- [ ] 终端字体大小合适
- [ ] 网络连接正常（如果需要）
- [ ] 备用笔记本电脑准备好
- [ ] 演示时间控制在30分钟内
- [ ] PPT或演示文档已准备
- [ ] 测试报告可以随时打开

---

**祝演示顺利！** 🎉
