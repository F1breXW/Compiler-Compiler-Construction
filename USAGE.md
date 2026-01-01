# 编译器测试工具使用说明

## ✅ 已实现的课程要求

### 1. 自动生成词法分析器和语法分析器 ✓
- **实现方式**: 从JSON配置文件读取文法规则，自动生成DFA词法分析器和LALR(1)语法分析器
- **文件**: `main.py` - 主程序演示

### 2. 测试词法和语法分析器（从文件读取源程序）✓
- **输出内容**:
  - ✅ 合法性判断
  - ✅ 产生式序列
  - ✅ 语法树（树形结构 + JSON + DOT可视化）
- **文件**: `test_from_file.py` - 从文件读取测试

### 3. LALR(1)分析表可视化 ✓
- **功能**: 生成ACTION表和GOTO表的HTML可视化
- **文件**: `visualize_table.py` - 分析表可视化工具

---

## 📝 使用方法

### ⚠️ Windows终端中文显示修复

由于Windows PowerShell默认编码问题，运行前请先执行：

```powershell
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

或者直接在每条命令前加上：
```powershell
$OutputEncoding = [System.Text.Encoding]::UTF8; python xxx.py
```

---

## 1. 主程序演示（内置测试用例）

```bash
python main.py
```

**功能**:
- 自动加载 `configs/` 目录下的所有文法配置
- 生成词法分析器和语法分析器  
- 运行配置中的测试用例
- 输出产生式序列和语法树

---

## 2. 从文件测试（课程要求的核心功能）

### 测试单个源程序文件

```bash
python test_from_file.py configs/grammar1_arithmetic.json test_programs/arithmetic_1.txt
```

**输出示例**:
```
======================================================================
[测试文件] test_programs/arithmetic_1.txt
[源程序] id + id * id
======================================================================

使用文法: 算术表达式文法

[词法分析结果]
  Token序列: [('id', 'id'), ('+', '+'), ('id', 'id'), ('*', '*'), ('id', 'id')]

[分析结果] 合法语句

[产生式序列] 共9步:
  1. F -> id
  2. T -> F
  3. E -> T
  4. F -> id
  5. T -> F
  6. F -> id
  7. T -> T * F
  8. E -> E + T
  9. S -> E

[语法树结构]
S [S -> E]
  E [E -> E + T]
    E [E -> T]
      T [T -> F]
        F [F -> id]
          id (id)
    + (+)
    T [T -> T * F]
      ...

[已保存] 语法树: generated/arithmetic_1_tree.json
[已保存] 可视化: visualizations/arithmetic_1_tree.dot
```

### 批量测试目录下的所有文件

```bash
python test_from_file.py configs/grammar1_arithmetic.json test_programs/ --batch
```

### 简洁模式（只显示结果）

```bash
python test_from_file.py configs/grammar1_arithmetic.json test_programs/arithmetic_1.txt --quiet
```

---

## 3. 生成LALR(1)分析表可视化

```bash
python visualize_table.py configs/grammar1_arithmetic.json
```

**输出**: `visualizations/算术表达式文法_lalr_table.html`

打开HTML文件即可看到：
- **ACTION表**: Shift/Reduce/Accept操作
- **GOTO表**: 状态转移
- **产生式列表**: 完整的文法规则
- **搜索功能**: 可按状态或符号搜索

---

## 4. 语法树可视化

语法树会自动保存为两种格式：

### DOT格式（推荐）
- **文件**: `visualizations/*_tree.dot`
- **在线查看**: 访问 [GraphvizOnline](https://dreampuf.github.io/GraphvizOnline/)
- **操作**: 将.dot文件内容粘贴到网站，即可看到图形化的语法树

### JSON格式
- **文件**: `generated/*_tree.json`
- **用途**: 程序化处理或调试

---

## 📂 目录结构

```
.
├── configs/                    # 文法配置文件（JSON）
│   ├── grammar1_arithmetic.json   # 算术表达式文法
│   ├── grammar2_assignment.json   # 赋值语句文法
│   └── grammar3_pl0.json          # PL/0文法
│
├── test_programs/             # 测试源程序（自定义）
│   ├── arithmetic_1.txt
│   ├── arithmetic_2.txt
│   └── ...
│
├── generated/                 # 生成的输出文件
│   ├── *_tree.json           # 语法树JSON
│   └── *.json                # 分析表等
│
├── visualizations/            # 可视化文件
│   ├── *_tree.dot            # 语法树DOT
│   ├── *_dfa.dot             # DFA图
│   └── *_lalr_table.html     # LALR分析表
│
├── main.py                    # 主程序（内置测试）
├── test_from_file.py          # 从文件测试（课程要求）
├── visualize_table.py         # 分析表可视化
└── view_tree.html             # 语法树在线查看器
```

---

## 🎯 测试示例文件

已提供的测试文件（在 `test_programs/` 目录）：

| 文件 | 内容 | 文法 |
|------|------|------|
| `arithmetic_1.txt` | `id + id * id` | 算术表达式 |
| `arithmetic_2.txt` | `( id + id ) * id` | 算术表达式 |
| `arithmetic_3.txt` | `id * ( id + id )` | 算术表达式 |
| `assignment_1.txt` | `x := id + id` | 赋值语句 |
| `assignment_2.txt` | `result := id - num` | 赋值语句 |

### 添加自定义测试文件

1. 在 `test_programs/` 目录创建 `.txt` 文件
2. 写入源程序（单行或多行）
3. 运行 `test_from_file.py` 测试

---

## 💡 常见问题

### Q1: 为什么终端显示乱码？
**A**: Windows PowerShell编码问题，运行前执行：
```powershell
$OutputEncoding = [System.Text.Encoding]::UTF8
```

### Q2: 如何查看语法树图形？
**A**: 两种方式：
1. 将 `.dot` 文件上传到 [GraphvizOnline](https://dreampuf.github.io/GraphvizOnline/)
2. 安装Graphviz后运行: `dot -Tpng tree.dot -o tree.png`

### Q3: 如何测试自己的文法？
**A**: 在 `configs/` 目录添加JSON配置文件，参考已有配置格式

### Q4: 分析表太大看不清？
**A**: 打开HTML文件后使用浏览器缩放（Ctrl + 滚轮）或使用搜索功能

---

## 📊 设计模式

项目中应用的设计模式：

1. **Facade模式**: CompilerGenerator - 统一接口
2. **Builder模式**: ParseTreeBuilder - 构建语法树  
3. **Composite模式**: ParseTreeNode - 树形结构
4. **Strategy模式**: LexicalGenerator/ParserGenerator - 算法封装
5. **Visitor模式**: ParseTreeVisualizer - 多格式输出

---

## 📞 总结

✅ **所有课程要求已完整实现**:

1. ✅ 自动生成词法分析器和语法分析器
2. ✅ 从文件读取源程序测试
3. ✅ 输出合法性判断
4. ✅ 输出产生式序列  
5. ✅ 生成并可视化语法树
6. ✅ LALR(1)分析表可视化

**核心测试命令**（记得设置UTF-8编码）:
```bash
# 设置编码
$OutputEncoding = [System.Text.Encoding]::UTF8

# 测试源程序
python test_from_file.py configs/grammar1_arithmetic.json test_programs/arithmetic_1.txt

# 生成分析表
python visualize_table.py configs/grammar1_arithmetic.json
```
