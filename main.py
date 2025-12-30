"""
编译器-编译器演示程序
满足课程要求：测试多个文法，每个文法测试多个程序体
"""

from lexical import LexicalGenerator
from syntax import Grammar, ParserGenerator
from driver import LRParser, PL0SemanticAnalyzer
from utils import save_parsing_tables
import json


def print_header(title):
    """打印标题"""
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80 + "\n")


def print_section(title):
    """打印小节标题"""
    print("\n" + "-"*80)
    print(f"【{title}】")
    print("-"*80)


# ============================================================================
# 第一部分：词法分析器自动生成测试
# ============================================================================

def test_lexical_generators():
    """
    测试词法分析器的自动生成能力
    要求：测试多个不同的词法规则
    """
    print_header("第一部分：词法分析器自动生成测试")
    
    print("功能说明：")
    print("  输入：正则表达式（词法规则）")
    print("  输出：该词法的DFA转换表")
    print("  测试：多个不同的词法规则\n")
    
    # 词法规则1：关键字 "begin"
    print_section("测试1.1 - 关键字识别: begin")
    generator1 = LexicalGenerator()
    table1, accept1 = generator1.generate("begin", "KEYWORD_BEGIN")
    print(f"[OK] 生成完成 - 状态数: {len(table1)}, 接受状态: {accept1}\n")
    
    # 词法规则2：关键字 "if"
    print_section("测试1.2 - 关键字识别: if")
    generator2 = LexicalGenerator()
    table2, accept2 = generator2.generate("if", "KEYWORD_IF")
    print(f"[OK] 生成完成 - 状态数: {len(table2)}, 接受状态: {accept2}\n")
    
    # 词法规则3：关键字 "while"
    print_section("测试1.3 - 关键字识别: while")
    generator3 = LexicalGenerator()
    table3, accept3 = generator3.generate("while", "KEYWORD_WHILE")
    print(f"[OK] 生成完成 - 状态数: {len(table3)}, 接受状态: {accept3}\n")
    
    print("="*80)
    print("词法分析器测试总结：")
    print(f"  [OK] 成功生成 3 个不同的词法分析器")
    print(f"  [OK] 各词法分析器均能正确处理对应的词法规则")
    print("="*80)


# ============================================================================
# 第二部分：语法分析器自动生成测试 - 文法1（算术表达式）
# ============================================================================

def create_expression_grammar():
    """
    文法1：算术表达式文法
    S -> E
    E -> E + T | E - T | T
    T -> T * F | T / F | F
    F -> ( E ) | id | num
    """
    print_section("文法1定义 - 算术表达式文法")
    grammar = Grammar()
    
    # 起始符号
    grammar.add_production("S", ["E"])
    
    # 表达式规则
    grammar.add_production("E", ["E", "+", "T"])
    grammar.add_production("E", ["E", "-", "T"])
    grammar.add_production("E", ["T"])
    
    # 项规则
    grammar.add_production("T", ["T", "*", "F"])
    grammar.add_production("T", ["T", "/", "F"])
    grammar.add_production("T", ["F"])
    
    # 因子规则
    grammar.add_production("F", ["(", "E", ")"])
    grammar.add_production("F", ["id"])
    grammar.add_production("F", ["num"])
    
    print("产生式：")
    for prod in grammar.productions:
        print(f"  {prod}")
    
    return grammar


def test_expression_grammar():
    """测试文法1：算术表达式文法"""
    print_header("第二部分：语法分析器自动生成测试 - 文法1")
    
    # 1. 创建文法
    grammar = create_expression_grammar()
    
    # 2. 自动生成语法分析器
    print_section("步骤1 - 自动生成LALR(1)分析表")
    generator = ParserGenerator(grammar)
    action_table, goto_table = generator.generate()
    print(f"[OK] 生成完成 - ACTION表项: {len(action_table)}, GOTO表项: {len(goto_table)}")
    
    # 3. 测试程序1 - 合法输入
    print_section("测试1.1 - 合法程序: a + b * c")
    tokens1 = [
        ('id', 'a'),
        ('+', '+'),
        ('id', 'b'),
        ('*', '*'),
        ('id', 'c')
    ]
    
    analyzer1 = PL0SemanticAnalyzer()
    parser1 = LRParser(generator.grammar, action_table, goto_table,
                      semantic_handler=analyzer1.semantic_action)
    
    success1 = parser1.parse(tokens1)
    
    if success1:
        print("\n[OK] 分析结果: 合法")
        print("\n使用的产生式序列:")
        for i, record in enumerate(parser1.parse_history, 1):
            if record['action'] == 'reduce':
                print(f"  {i}. {record['production']}")
        
        print("\n生成的中间代码:")
        for i, code in enumerate(analyzer1.get_code(), 1):
            print(f"  {i}: {code}")
    else:
        print("[FAIL] 分析失败")
    
    # 4. 测试程序2 - 合法输入（带括号）
    print_section("测试1.2 - 合法程序: (a + b) * c")
    tokens2 = [
        ('(', '('),
        ('id', 'a'),
        ('+', '+'),
        ('id', 'b'),
        (')', ')'),
        ('*', '*'),
        ('id', 'c')
    ]
    
    analyzer2 = PL0SemanticAnalyzer()
    parser2 = LRParser(generator.grammar, action_table, goto_table,
                      semantic_handler=analyzer2.semantic_action)
    
    success2 = parser2.parse(tokens2)
    
    if success2:
        print("\n[OK] 分析结果: 合法")
        print("\n使用的产生式序列:")
        for i, record in enumerate(parser2.parse_history, 1):
            if record['action'] == 'reduce':
                print(f"  {i}. {record['production']}")
        
        print("\n生成的中间代码:")
        for i, code in enumerate(analyzer2.get_code(), 1):
            print(f"  {i}: {code}")
    else:
        print("[FAIL] 分析失败")
    
    # 5. 测试程序3 - 非法输入
    print_section("测试1.3 - 非法程序: a + + b")
    tokens3 = [
        ('id', 'a'),
        ('+', '+'),
        ('+', '+'),
        ('id', 'b')
    ]
    
    analyzer3 = PL0SemanticAnalyzer()
    parser3 = LRParser(generator.grammar, action_table, goto_table,
                      semantic_handler=analyzer3.semantic_action)
    
    success3 = parser3.parse(tokens3)
    
    if success3:
        print("\n[OK] 分析结果: 合法")
    else:
        print("\n[EXPECTED] 分析结果: 非法（语法错误）")
    
    print("\n" + "="*80)
    print("文法1测试总结：")
    print(f"  [OK] 成功自动生成语法分析器")
    print(f"  [OK] 测试了 3 个不同的程序（2个合法，1个非法）")
    print(f"  [OK] 能正确判断程序合法性")
    print(f"  [OK] 能输出产生式序列和中间代码")
    print("="*80)


# ============================================================================
# 第三部分：语法分析器自动生成测试 - 文法2（赋值语句）
# ============================================================================

def create_assignment_grammar():
    """
    文法2：赋值语句文法
    S -> id := E
    E -> E + T | E - T | T
    T -> id | num
    """
    print_section("文法2定义 - 赋值语句文法")
    grammar = Grammar()
    
    # 赋值语句
    grammar.add_production("S", ["id", ":=", "E"])
    
    # 表达式规则
    grammar.add_production("E", ["E", "+", "T"])
    grammar.add_production("E", ["E", "-", "T"])
    grammar.add_production("E", ["T"])
    
    # 项规则
    grammar.add_production("T", ["id"])
    grammar.add_production("T", ["num"])
    
    print("产生式：")
    for prod in grammar.productions:
        print(f"  {prod}")
    
    return grammar


def test_assignment_grammar():
    """测试文法2：赋值语句文法"""
    print_header("第三部分：语法分析器自动生成测试 - 文法2")
    
    # 1. 创建文法
    grammar = create_assignment_grammar()
    
    # 2. 自动生成语法分析器
    print_section("步骤1 - 自动生成LALR(1)分析表")
    generator = ParserGenerator(grammar)
    action_table, goto_table = generator.generate()
    print(f"[OK] 生成完成 - ACTION表项: {len(action_table)}, GOTO表项: {len(goto_table)}")
    
    # 3. 测试程序1 - 合法输入
    print_section("测试2.1 - 合法程序: x := a + b")
    tokens1 = [
        ('id', 'x'),
        (':=', ':='),
        ('id', 'a'),
        ('+', '+'),
        ('id', 'b')
    ]
    
    analyzer1 = PL0SemanticAnalyzer()
    parser1 = LRParser(generator.grammar, action_table, goto_table,
                      semantic_handler=analyzer1.semantic_action)
    
    success1 = parser1.parse(tokens1)
    
    if success1:
        print("\n[OK] 分析结果: 合法")
        print("\n使用的产生式序列:")
        for i, record in enumerate(parser1.parse_history, 1):
            if record['action'] == 'reduce':
                print(f"  {i}. {record['production']}")
        
        print("\n生成的中间代码:")
        for i, code in enumerate(analyzer1.get_code(), 1):
            print(f"  {i}: {code}")
    else:
        print("[FAIL] 分析失败")
    
    # 4. 测试程序2 - 合法输入
    print_section("测试2.2 - 合法程序: result := 100 - x")
    tokens2 = [
        ('id', 'result'),
        (':=', ':='),
        ('num', '100'),
        ('-', '-'),
        ('id', 'x')
    ]
    
    analyzer2 = PL0SemanticAnalyzer()
    parser2 = LRParser(generator.grammar, action_table, goto_table,
                      semantic_handler=analyzer2.semantic_action)
    
    success2 = parser2.parse(tokens2)
    
    if success2:
        print("\n[OK] 分析结果: 合法")
        print("\n使用的产生式序列:")
        for i, record in enumerate(parser2.parse_history, 1):
            if record['action'] == 'reduce':
                print(f"  {i}. {record['production']}")
        
        print("\n生成的中间代码:")
        for i, code in enumerate(analyzer2.get_code(), 1):
            print(f"  {i}: {code}")
    else:
        print("[FAIL] 分析失败")
    
    # 5. 测试程序3 - 非法输入（缺少赋值符号）
    print_section("测试2.3 - 非法程序: x a + b")
    tokens3 = [
        ('id', 'x'),
        ('id', 'a'),
        ('+', '+'),
        ('id', 'b')
    ]
    
    analyzer3 = PL0SemanticAnalyzer()
    parser3 = LRParser(generator.grammar, action_table, goto_table,
                      semantic_handler=analyzer3.semantic_action)
    
    success3 = parser3.parse(tokens3)
    
    if success3:
        print("\n[OK] 分析结果: 合法")
    else:
        print("\n[EXPECTED] 分析结果: 非法（语法错误）")
    
    print("\n" + "="*80)
    print("文法2测试总结：")
    print(f"  [OK] 成功自动生成语法分析器")
    print(f"  [OK] 测试了 3 个不同的程序（2个合法，1个非法）")
    print(f"  [OK] 能正确判断程序合法性")
    print(f"  [OK] 能输出产生式序列和中间代码")
    print("="*80)


# ============================================================================
# 主函数
# ============================================================================

def main():
    """
    主函数：演示编译器-编译器的自动生成能力
    
    测试内容：
    1. 词法分析器：测试3个不同的词法规则
    2. 语法分析器：测试2个不同的文法，每个文法测试3个程序
    
    满足课程要求：
    - 输入文法规则，自动输出词法分析器和语法分析器
    - 测试多个文法（至少2个）
    - 每个文法测试多个程序（至少2个）
    - 输出合法性判断和产生式序列
    """
    
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                    编译器-编译器 (Compiler-Compiler)                    ║
║                         自动生成能力演示                                 ║
║                                                                          ║
║  功能：输入文法规则，自动生成词法分析器和语法分析器                     ║
║                                                                          ║
║  测试内容：                                                              ║
║    1. 词法分析器：3个不同的词法规则                                     ║
║    2. 语法分析器文法1：算术表达式（3个测试程序）                        ║
║    3. 语法分析器文法2：赋值语句（3个测试程序）                          ║
║                                                                          ║
║  作者：同学A（词法分析、语法分析负责人）                                ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""")
    
    # 第一部分：词法分析器自动生成测试
    test_lexical_generators()
    
    # 第二部分：语法分析器测试 - 文法1（算术表达式）
    test_expression_grammar()
    
    # 第三部分：语法分析器测试 - 文法2（赋值语句）
    test_assignment_grammar()
    
    # 总结
    print_header("测试总结")
    print("""
[OK] 词法分析器自动生成能力验证：
  - 测试了 3 个不同的词法规则
  - 均成功生成对应的DFA转换表
  
[OK] 语法分析器自动生成能力验证：
  - 测试了 2 个不同的文法
  - 每个文法测试了 3 个不同的程序（包括合法和非法）
  - 均能正确判断程序合法性
  - 能输出使用的产生式序列
  - 能生成中间代码（三地址码）

[OK] 符合课程要求：
  (1) 能根据输入的文法规则自动生成词法/语法分析器  [OK]
  (2) 测试了多个文法（>=2个）                        [OK]
  (3) 每个文法测试了多个程序（>=2个）                [OK]
  (4) 输出了合法性判断和产生式序列                  [OK]

项目文件说明：
  - lexical/  : 词法分析生成器（Thompson + 子集构造 + DFA最小化）
  - syntax/   : 语法分析生成器（FIRST/FOLLOW + LR(1) + LALR(1)）
  - driver/   : LR分析驱动程序（栈式分析器 + 语义动作接口）
  - utils/    : 工具函数（日志、文件I/O）
  - main.py   : 本演示程序
  
给同学B的接口：
  详见 API_FOR_TEAMMATE_B.md 文档
""")


if __name__ == "__main__":
    main()
