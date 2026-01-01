# 中间代码生成测试

本目录包含用于测试编译器中间代码生成功能的测试脚本。

## 文件说明

### test_ic_generation.py
中间代码生成测试脚本（主要测试工具），用于测试单个源程序文件。

**功能：**
- 词法分析 + 语法分析 + 语义分析
- 生成三地址码
- 显示符号表
- 输出详细的分析过程
- 自动保存IR文件到 `generated/` 目录

**使用方法：**
```bash
python tests/intermediate_code/test_ic_generation.py <文法配置> <源程序文件>

# 示例
python tests/intermediate_code/test_ic_generation.py configs/grammar_imperative.json test_programs/intermediate_code/ic_test1_arithmetic.txt
```

### run_all_ic_tests.py
批量测试脚本，自动运行所有中间代码生成测试用例。

**功能：**
- 自动运行所有4个测试用例
- 汇总测试结果
- 显示通过率统计

**使用方法：**
```bash
python tests/intermediate_code/run_all_ic_tests.py
```

### test_ic_basic.py
基础中间代码生成测试脚本。

## 测试用例

测试程序位于 `test_programs/intermediate_code/` 目录：

| 文件 | 测试内容 | 生成代码 |
|------|---------|---------|
| ic_test1_arithmetic.txt | 类型检查和算术运算 | 5条 |
| ic_test2_if_else.txt | if/else条件语句 | 17条 |
| ic_test3_while_loop.txt | while循环结构 | 13条 |
| ic_test4_complex_bool.txt | 复杂布尔表达式 | 23条 |

## 测试报告

测试报告保存在 `reports/` 目录：
- **ADVANCED_TEST_REPORT.md** - 详细的测试报告，包含所有测试用例的结果和分析
- **test_results_advanced.txt** - 完整的测试输出日志

## 验证的功能

### 1. 类型系统
- ✓ int/bool类型声明
- ✓ 类型检查
- ✓ 类型不匹配错误检测

### 2. 符号表管理
- ✓ 变量声明记录
- ✓ 类型信息存储
- ✓ 初始化状态跟踪
- ✓ 重复声明检测

### 3. 三地址码生成
- ✓ 临时变量分配（t1, t2, ...）
- ✓ 标签生成（L1, L2, ...）
- ✓ 运算符优先级处理

### 4. 控制流语句
- ✓ if单分支语句
- ✓ if-else双分支语句
- ✓ while循环
- ✓ 复合语句块（{}）

### 5. 回填技术
- ✓ truelist/falselist管理
- ✓ 条件跳转回填
- ✓ 标签地址回填

### 6. 布尔表达式
- ✓ 关系运算符（<, >, <=, >=, ==, !=）
- ✓ 逻辑与（&&）
- ✓ 逻辑或（||）
- ✓ 逻辑非（!）

## 快速开始

```bash
# 1. 运行单个测试
cd E:\code\project\Compiler-Compiler Construction\Compiler-Compiler-Construction
python tests/semantic_analysis/test_advanced.py configs/grammar_imperative.json test_programs/intermediate_code/advanced_test1.txt

# 2. 运行所有测试
python tests/semantic_analysis/test_all_advanced.py

# 3. 查看测试报告
# 打开 reports/ADVANCED_TEST_REPORT.md
```

## 注意事项

1. 确保已安装必要的依赖
2. 使用 `configs/grammar_imperative.json` 文法配置
3. 源程序文件需符合文法规范
4. Windows系统注意编码问题（已在脚本中处理）

## 测试结果

最新测试结果：**4/4 通过（100%）**

详见：[reports/ADVANCED_TEST_REPORT.md](../../reports/ADVANCED_TEST_REPORT.md)
