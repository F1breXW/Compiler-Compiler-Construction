# 语义分析接口使用指南

**目标用户：** 负责语义分析和中间代码生成部分的同学

---

## 概述

本文档介绍如何使用编译器生成器提供的语义分析接口，实现自定义的语义动作和中间代码生成。

核心思路：继承 `SemanticAnalyzer` 基类，重写 `semantic_action()` 方法，在归约时执行语义动作。

---

## 快速开始

### 1. 创建自定义语义分析器

```python
from driver import SemanticAnalyzer, Symbol
from syntax import Production

class MySemanticAnalyzer(SemanticAnalyzer):
    def semantic_action(self, production, symbols):
        """
        语义动作处理函数
        
        参数:
            production: 当前归约使用的产生式对象
            symbols: 归约的符号列表(每个符号有name和value属性)
        
        返回:
            该非终结符的综合属性值
        """
        # 示例: 处理加法表达式 E -> E + T
        if str(production) == "E -> E + T":
            left = symbols[0].value
            right = symbols[2].value
            temp = self.new_temp()
            self.emit(f"{temp} = {left} + {right}")
            return temp
        
        # 默认: 传递第一个符号的值
        return symbols[0].value if symbols else None
```

### 2. 使用语义分析器

```python
from driver import LRParser
from syntax import Grammar, ParserGenerator

# 创建文法和分析表
grammar = Grammar()
grammar.add_production("E", ["E", "+", "T"])
grammar.add_production("E", ["T"])
grammar.add_production("T", ["id"])

generator = ParserGenerator(grammar)
action_table, goto_table = generator.generate()

# 创建分析器并绑定语义动作
analyzer = MySemanticAnalyzer()
parser = LRParser(
    grammar, 
    action_table, 
    goto_table,
    semantic_handler=analyzer.semantic_action  # 绑定语义动作
)

# 执行分析
tokens = [('id', 'a'), ('+', '+'), ('id', 'b')]
success = parser.parse(tokens)

# 获取生成的中间代码
if success:
    code = analyzer.get_code()
    print("生成的三地址码:", code)
```

---

## SemanticAnalyzer 基类提供的工具函数

### 临时变量管理

```python
temp = self.new_temp()  # 生成临时变量名: t1, t2, t3, ...
```

### 中间代码生成

```python
self.emit("t1 = a + b")  # 生成一条三地址码
self.emit("if t1 goto L1")
self.emit("L1:")
```

### 符号表管理

```python
# 添加符号
self.add_symbol("x", "int")
self.add_symbol("y", 10)

# 查询符号
value = self.lookup_symbol("x")  # 返回 "int" 或 None
```

### 输出辅助函数

```python
# 获取生成的所有中间代码
code_list = self.get_code()

# 打印符号表
self.print_symbol_table()

# 打印生成的中间代码
self.print_intermediate_code()
```

---

## 产生式匹配技巧

### 方法1: 字符串匹配（推荐）

```python
def semantic_action(self, production, symbols):
    prod_str = str(production)  # 转换为字符串格式: "E -> E + T"
    
    if prod_str == "E -> E + T":
        # 处理加法
        pass
    elif prod_str == "T -> T * F":
        # 处理乘法
        pass
    elif prod_str == "S -> id := E":
        # 处理赋值
        pass
```

### 方法2: 检查产生式ID

```python
def semantic_action(self, production, symbols):
    # 产生式按添加顺序编号: 0, 1, 2, ...
    if production.id == 1:  # 第2个产生式 (E -> E + T)
        pass
    elif production.id == 4:  # 第5个产生式 (T -> T * F)
        pass
```

### 方法3: 检查产生式结构

```python
def semantic_action(self, production, symbols):
    # 检查左部
    if production.left == "E":
        # 检查右部长度和符号
        if len(symbols) == 3 and symbols[1].name == '+':
            # E -> E + T
            pass
        elif len(symbols) == 3 and symbols[1].name == '-':
            # E -> E - T
            pass
```

---

## 符号栈使用详解

### 符号对象结构

每个 `Symbol` 对象包含：
- `name`: 符号名称（终结符或非终结符）
- `value`: 符号的语义值
- `attributes`: 附加属性字典（可选）

### 访问归约符号

归约时，`symbols` 参数是一个列表，从左到右对应产生式右部的符号。

**示例：归约 E → E + T**

```python
def semantic_action(self, production, symbols):
    if str(production) == "E -> E + T":
        # symbols[0]: E (左操作数)
        # symbols[1]: + (操作符)
        # symbols[2]: T (右操作数)
        
        left_value = symbols[0].value    # 左表达式的值
        operator = symbols[1].name       # "+"
        right_value = symbols[2].value   # 右项的值
        
        # 生成三地址码
        temp = self.new_temp()
        self.emit(f"{temp} = {left_value} {operator} {right_value}")
        
        return temp  # 返回综合属性
```

### 访问属性

```python
# 获取符号的附加属性
if 'type' in symbols[0].attributes:
    var_type = symbols[0].attributes['type']

# 设置返回值的属性（通过修改符号栈）
result = Symbol("E", temp)
result.attributes['type'] = 'int'
```

---

## 完整示例：算术表达式语义分析

```python
from driver import SemanticAnalyzer, LRParser
from syntax import Grammar, ParserGenerator

class ExpressionAnalyzer(SemanticAnalyzer):
    """算术表达式的语义分析器"""
    
    def semantic_action(self, production, symbols):
        prod_str = str(production)
        
        # E -> E + T (加法)
        if prod_str == "E -> E + T":
            left = symbols[0].value
            right = symbols[2].value
            temp = self.new_temp()
            self.emit(f"{temp} = {left} + {right}")
            return temp
        
        # E -> E - T (减法)
        elif prod_str == "E -> E - T":
            left = symbols[0].value
            right = symbols[2].value
            temp = self.new_temp()
            self.emit(f"{temp} = {left} - {right}")
            return temp
        
        # T -> T * F (乘法)
        elif prod_str == "T -> T * F":
            left = symbols[0].value
            right = symbols[2].value
            temp = self.new_temp()
            self.emit(f"{temp} = {left} * {right}")
            return temp
        
        # T -> T / F (除法)
        elif prod_str == "T -> T / F":
            left = symbols[0].value
            right = symbols[2].value
            temp = self.new_temp()
            self.emit(f"{temp} = {left} / {right}")
            return temp
        
        # E -> T, T -> F (值传递)
        elif prod_str in ["E -> T", "T -> F"]:
            return symbols[0].value
        
        # F -> ( E ) (括号表达式)
        elif prod_str == "F -> ( E )":
            return symbols[1].value  # 返回括号内表达式的值
        
        # F -> id (标识符)
        elif prod_str == "F -> id":
            return symbols[0].value
        
        # F -> num (数字)
        elif prod_str == "F -> num":
            return symbols[0].value
        
        # 默认
        return None


# 使用示例
def main():
    # 1. 定义文法
    grammar = Grammar()
    grammar.add_production("S", ["E"])
    grammar.add_production("E", ["E", "+", "T"])
    grammar.add_production("E", ["E", "-", "T"])
    grammar.add_production("E", ["T"])
    grammar.add_production("T", ["T", "*", "F"])
    grammar.add_production("T", ["T", "/", "F"])
    grammar.add_production("T", ["F"])
    grammar.add_production("F", ["(", "E", ")"])
    grammar.add_production("F", ["id"])
    grammar.add_production("F", ["num"])
    
    # 2. 生成分析表
    generator = ParserGenerator(grammar)
    action_table, goto_table = generator.generate()
    
    # 3. 创建语义分析器
    analyzer = ExpressionAnalyzer()
    
    # 4. 创建分析器
    parser = LRParser(
        generator.grammar,
        action_table,
        goto_table,
        semantic_handler=analyzer.semantic_action
    )
    
    # 5. 分析表达式: a + b * c
    tokens = [
        ('id', 'a'),
        ('+', '+'),
        ('id', 'b'),
        ('*', '*'),
        ('id', 'c')
    ]
    
    success = parser.parse(tokens)
    
    # 6. 查看结果
    if success:
        print("分析成功!")
        analyzer.print_intermediate_code()
        # 输出:
        #   1: t1 = b * c
        #   2: t2 = a + t1

if __name__ == '__main__':
    main()
```

---

## 完整示例：赋值语句语义分析

```python
class AssignmentAnalyzer(SemanticAnalyzer):
    """赋值语句的语义分析器"""
    
    def semantic_action(self, production, symbols):
        prod_str = str(production)
        
        # S -> id := E (赋值语句)
        if ":=" in prod_str:
            var_name = symbols[0].value
            expr_value = symbols[2].value
            self.emit(f"{var_name} = {expr_value}")
            return None
        
        # E -> E + T (加法)
        elif prod_str == "E -> E + T":
            left = symbols[0].value
            right = symbols[2].value
            temp = self.new_temp()
            self.emit(f"{temp} = {left} + {right}")
            return temp
        
        # E -> T (传递)
        elif prod_str == "E -> T":
            return symbols[0].value
        
        # T -> id (标识符)
        elif prod_str == "T -> id":
            return symbols[0].value
        
        # T -> num (数字)
        elif prod_str == "T -> num":
            return symbols[0].value
        
        return None


# 使用示例
grammar = Grammar()
grammar.add_production("S", ["id", ":=", "E"])
grammar.add_production("E", ["E", "+", "T"])
grammar.add_production("E", ["T"])
grammar.add_production("T", ["id"])
grammar.add_production("T", ["num"])

generator = ParserGenerator(grammar)
action_table, goto_table = generator.generate()

analyzer = AssignmentAnalyzer()
parser = LRParser(generator.grammar, action_table, goto_table, 
                 semantic_handler=analyzer.semantic_action)

# 分析: x := a + b
tokens = [
    ('id', 'x'),
    (':=', ':='),
    ('id', 'a'),
    ('+', '+'),
    ('id', 'b')
]

if parser.parse(tokens):
    analyzer.print_intermediate_code()
    # 输出:
    #   1: t1 = a + b
    #   2: x = t1
```

---

## 高级技巧

### 1. 类型检查

```python
def semantic_action(self, production, symbols):
    if str(production) == "E -> E + T":
        left_type = symbols[0].attributes.get('type', 'unknown')
        right_type = symbols[2].attributes.get('type', 'unknown')
        
        if left_type != right_type:
            print(f"警告: 类型不匹配 {left_type} + {right_type}")
        
        temp = self.new_temp()
        self.emit(f"{temp} = {symbols[0].value} + {symbols[2].value}")
        
        # 设置结果类型
        result = Symbol("E", temp)
        result.attributes['type'] = left_type
        return result
```

### 2. 短路求值（逻辑表达式）

```python
def semantic_action(self, production, symbols):
    # E -> E and E
    if "and" in str(production):
        left = symbols[0].value
        right = symbols[2].value
        
        # 生成短路代码
        false_label = self.new_label()
        end_label = self.new_label()
        temp = self.new_temp()
        
        self.emit(f"if not {left} goto {false_label}")
        self.emit(f"if not {right} goto {false_label}")
        self.emit(f"{temp} = true")
        self.emit(f"goto {end_label}")
        self.emit(f"{false_label}:")
        self.emit(f"{temp} = false")
        self.emit(f"{end_label}:")
        
        return temp
```

### 3. 符号表作用域管理

```python
class ScopedAnalyzer(SemanticAnalyzer):
    def __init__(self):
        super().__init__()
        self.scope_stack = [{}]  # 作用域栈
    
    def enter_scope(self):
        self.scope_stack.append({})
    
    def exit_scope(self):
        self.scope_stack.pop()
    
    def add_symbol_scoped(self, name, value):
        self.scope_stack[-1][name] = value
    
    def lookup_symbol_scoped(self, name):
        # 从内到外查找
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None
```

---

## 常见问题

### Q1: 如何调试语义动作？

在 `semantic_action()` 中添加打印语句：

```python
def semantic_action(self, production, symbols):
    print(f"[调试] 产生式: {production}")
    print(f"[调试] 符号: {[s.name + ':' + str(s.value) for s in symbols]}")
    # ... 你的代码
```

### Q2: 如何处理ε产生式？

ε产生式归约时，`symbols` 为空列表：

```python
def semantic_action(self, production, symbols):
    if str(production) == "A -> ε":
        # symbols 是空列表
        return None  # 返回默认值
```

### Q3: 如何生成四元式而不是三地址码？

```python
def emit_quad(self, op, arg1, arg2, result):
    """生成四元式: (op, arg1, arg2, result)"""
    quad = f"({op}, {arg1}, {arg2}, {result})"
    self.intermediate_code.append(quad)
```

---

## 接口文档总结

| 接口 | 功能 | 示例 |
|------|------|------|
| `semantic_action(production, symbols)` | 主要接口，重写此方法 | 见上文示例 |
| `new_temp()` | 生成临时变量 | `t1 = self.new_temp()` |
| `emit(code)` | 生成一条中间代码 | `self.emit("t1 = a + b")` |
| `add_symbol(name, value)` | 添加符号 | `self.add_symbol("x", "int")` |
| `lookup_symbol(name)` | 查询符号 | `val = self.lookup_symbol("x")` |
| `get_code()` | 获取所有中间代码 | `code_list = self.get_code()` |
| `print_symbol_table()` | 打印符号表 | `self.print_symbol_table()` |
| `print_intermediate_code()` | 打印中间代码 | `self.print_intermediate_code()` |

---

## 参考资料

- 主程序示例：`main.py`
- 语义分析器基类源码：`driver/semantic_analyzer.py`
- PL/0示例实现：`driver/pl0_analyzer.py`
- LR分析驱动程序：`driver/lr_parser.py`

---

**作者：** 核心算法引擎负责人 
**适用版本：** Python 3.7+  
**更新日期：** 2025年12月30日
