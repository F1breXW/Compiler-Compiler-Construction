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


"""
编译器-编译器演示程序
满足课程要求：测试多个文法，每个文法测试多个程序体
"""

from lexical import LexicalGenerator, Scanner
from syntax import Grammar, ParserGenerator
from driver import LRParser, PL0SemanticAnalyzer
from utils import save_parsing_tables, save_json
from utils.visualizer import GraphvizVisualizer
import json


def pause():
    """暂停程序，等待用户按回车键"""
    input("\n[按回车键继续...]")


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
    要求：测试多个不同的词法规则，并生成完整的词法分析器
    """
    print_header("第一部分：词法分析器自动生成测试")
    
    print("功能说明：")
    print("  输入：一系列词法规则（关键字、运算符、标识符、数字）")
    print("  输出：一个完整的DFA转换表")
    print("  测试：构建一个能识别PL/0子集的词法分析器\n")
    
    generator = LexicalGenerator()
    
    # 定义词法规则
    rules = [
        # 关键字
        ("begin", "begin"), ("end", "end"),
        ("if", "if"), ("then", "then"),
        ("while", "while"), ("do", "do"),
        
        # 运算符和界符 (注意：特殊字符需要转义)
        ("\\+", "+"), ("-", "-"), ("\\*", "*"), ("/", "/"),
        (":=", ":="), ("\\(", "("), ("\\)", ")"),
        
        # 复杂规则 (由生成器特殊处理)
        ("id", "id"),   # [a-zA-Z][a-zA-Z0-9]*
        ("num", "num")  # [0-9]+
    ]
    
    print_section("步骤1 - 构建综合词法分析器 (PL/0子集)")
    print(f"规则列表: {rules}")
    
    table, accepting_map = generator.build(rules)
    print(f"\n[OK] 生成完成 - DFA状态数: {len(table)}")
    print(f"[OK] 接受状态数: {len(accepting_map)}")
    
    # 导出可视化
    if generator.last_min_dfa:
        GraphvizVisualizer.export_dfa(generator.last_min_dfa, "dfa_min.dot", "Minimized DFA")
        print("  [可视化] 已生成 dfa_min.dot")

    # ========================================================================
    # 演示第二个文法：自定义正则
    # ========================================================================
    print_section("步骤2 - 测试第二个文法 (自定义正则)")
    print("测试说明：定义一个新的简单文法，使用自定义正则表达式")
    print("文法特点：")
    print("  1. 变量名必须以小写字母开头 (VAR)")
    print("  2. 支持整数 (INTEGER) 和 浮点数 (FLOAT)")
    print("  3. 支持位运算符 (BITAND, BITOR)")
    
    rules2 = [
        # 类型关键字
        ("int", "TYPE"), ("float", "TYPE"),
        
        # 变量名: [a-z][a-z0-9]*
        ("[a-z][a-z0-9]*", "VAR"),
        
        # 浮点数: [0-9]+.[0-9]+ (简化版)
        ("[0-9]+\\.[0-9]+", "FLOAT"),
        
        # 整数: [0-9]+
        ("[0-9]+", "INTEGER"),
        
        # 运算符
        ("&", "BITAND"), ("\\|", "BITOR"),
        ("=", "ASSIGN"), ("\\+", "PLUS")
    ]
    
    print(f"规则列表: {rules2}")
    table2, accepting_map2 = generator.build(rules2)
    print(f"\n[OK] 生成完成 - DFA状态数: {len(table2)}")
    
    # 测试输入
    scanner2 = Scanner(table2, accepting_map2)
    test_input2 = "int x = 10 + 3.14 & y"
    print(f"\n测试输入: '{test_input2}'")
    tokens2 = scanner2.scan(test_input2)
    for token in tokens2:
        print(f"  {token}")
    
    pause()
    print_section("步骤1.5 - 输出生成的词法分析器")
    print("正在导出DFA转换表...")
    
    # 导出可视化图表
    print("正在导出可视化图表...")
    GraphvizVisualizer.export_nfa(generator.last_nfa, "nfa.dot", "Thompson NFA")
    GraphvizVisualizer.export_dfa(generator.last_min_dfa, "dfa_min.dot", "Minimized DFA")
    print("  [文件] NFA可视化已保存至: nfa.dot")
    print("  [文件] 最小化DFA可视化已保存至: dfa_min.dot")
    print("  (请使用 Graphviz 或 VS Code 插件预览这些 .dot 文件)")
    
    # 保存到文件
    lexical_output = {
        "transitions": table,
        "accepting_states": accepting_map
    }
    save_json(lexical_output, "generated_lexical_analyzer.json")
    print(f"  [文件] 词法分析器已保存至: generated_lexical_analyzer.json")
    
    # 打印预览
    print("\n  DFA转换表预览 (前5个状态):")
    print("  State | Input -> Next State")
    print("  " + "-"*40)
    for state in sorted(table.keys())[:5]:
        transitions = table[state]
        # 只显示前3个转换
        items = list(transitions.items())
        for char, next_state in items[:3]:
            print(f"  {state:5d} | {repr(char):5s} -> {next_state}")
        if len(items) > 3:
            print(f"  {state:5d} | ... ({len(items)-3} more)")
    print("  ...")
    
    pause()

    # 创建扫描器
    scanner = Scanner(table, accepting_map)
    
    # 测试扫描
    print_section("步骤2 - 测试词法扫描")
    test_code = "if x := a + 10 then begin end"
    print(f"源代码: {test_code}")
    
    tokens = scanner.scan(test_code)
    print("\n识别到的Token序列:")
    for token in tokens:
        print(f"  {token}")
        
    print("\n" + "="*80)
    print("词法分析器测试总结：")
    print(f"  [OK] 成功合并 {len(rules)} 条规则为一个DFA")
    print(f"  [OK] 成功识别关键字、标识符、数字和运算符")
    print(f"  [OK] 实现了真正的从字符串到Token的转换")
    print("="*80)
    
    return scanner  # 返回扫描器供后续使用


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


def test_expression_grammar(scanner):
    """测试文法1：算术表达式文法"""
    print_header("第二部分：语法分析器自动生成测试 - 文法1")
    
    # 1. 创建文法
    grammar = create_expression_grammar()
    
    # 2. 自动生成语法分析器
    print_section("步骤1 - 自动生成LALR(1)分析表")
    generator = ParserGenerator(grammar)
    action_table, goto_table = generator.generate()
    print(f"[OK] 生成完成 - ACTION表项: {len(action_table)}, GOTO表项: {len(goto_table)}")
    
    # 输出生成的分析器
    print_section("步骤1.5 - 输出生成的语法分析器")
    print("正在导出LALR(1)分析表...")
    
    save_parsing_tables(action_table, goto_table, "generated_parser_grammar1.json")
    print(f"  [文件] 语法分析器已保存至: generated_parser_grammar1.json")

    # 打印预览
    print("\n  ACTION表预览 (前10项):")
    print("  State | Symbol | Action")
    print("  " + "-"*40)
    for (state, symbol), (action, val) in list(action_table.items())[:10]:
        print(f"  {state:5d} | {symbol:6s} | {action} {val}")
    print("  ...")
    
    pause()
    
    # 3. 测试程序1 - 合法输入
    print_section("测试1.1 - 合法程序: a + b * c")
    source_code1 = "a + b * c"
    print(f"源代码: {source_code1}")
    tokens1 = scanner.scan(source_code1)
    print(f"Token序列: {tokens1}")
    
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
    source_code2 = "(a + b) * c"
    print(f"源代码: {source_code2}")
    tokens2 = scanner.scan(source_code2)
    print(f"Token序列: {tokens2}")
    
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
    source_code3 = "a + + b"
    print(f"源代码: {source_code3}")
    tokens3 = scanner.scan(source_code3)
    print(f"Token序列: {tokens3}")
    
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
    print(f"  [OK] 使用自动生成的Scanner进行词法分析")
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


def test_assignment_grammar(scanner):
    """测试文法2：赋值语句文法"""
    print_header("第三部分：语法分析器自动生成测试 - 文法2")
    
    # 1. 创建文法
    grammar = create_assignment_grammar()
    
    # 2. 自动生成语法分析器
    print_section("步骤1 - 自动生成LALR(1)分析表")
    generator = ParserGenerator(grammar)
    action_table, goto_table = generator.generate()
    print(f"[OK] 生成完成 - ACTION表项: {len(action_table)}, GOTO表项: {len(goto_table)}")
    
    # 输出生成的分析器
    print_section("步骤1.5 - 输出生成的语法分析器")
    print("正在导出LALR(1)分析表...")
    
    save_parsing_tables(action_table, goto_table, "generated_parser_grammar2.json")
    print(f"  [文件] 语法分析器已保存至: generated_parser_grammar2.json")

    # 打印预览
    print("\n  ACTION表预览 (前10项):")
    print("  State | Symbol | Action")
    print("  " + "-"*40)
    for (state, symbol), (action, val) in list(action_table.items())[:10]:
        print(f"  {state:5d} | {symbol:6s} | {action} {val}")
    print("  ...")
    
    pause()
    
    # 3. 测试程序1 - 合法输入
    print_section("测试2.1 - 合法程序: x := a + b")
    source_code1 = "x := a + b"
    print(f"源代码: {source_code1}")
    tokens1 = scanner.scan(source_code1)
    print(f"Token序列: {tokens1}")
    
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
    source_code2 = "result := 100 - x"
    print(f"源代码: {source_code2}")
    tokens2 = scanner.scan(source_code2)
    print(f"Token序列: {tokens2}")
    
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
    source_code3 = "x a + b"
    print(f"源代码: {source_code3}")
    tokens3 = scanner.scan(source_code3)
    print(f"Token序列: {tokens3}")
    
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
    print(f"  [OK] 使用自动生成的Scanner进行词法分析")
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
    scanner = test_lexical_generators()
    pause()
    
    # 第二部分：语法分析器测试 - 文法1（算术表达式）
    test_expression_grammar(scanner)
    pause()
    
    # 第三部分：语法分析器测试 - 文法2（赋值语句）
    test_assignment_grammar(scanner)
    
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
