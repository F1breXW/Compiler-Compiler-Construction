"""
编译器生成器主程序
演示如何使用词法生成器和语法生成器处理PL/0语言
"""

from lexical import LexicalGenerator
from syntax import Grammar, ParserGenerator, Production
from driver import LRParser, PL0SemanticAnalyzer, Symbol
from utils import save_parsing_tables
import json


def create_pl0_grammar() -> Grammar:
    """
    创建PL/0语言的简化文法
    
    PL/0语法规则(简化版):
    program -> block .
    block -> [ const-declaration ] [ var-declaration ] statement
    statement -> id := expression
               | if condition then statement
               | while condition do statement
               | begin statement { ; statement } end
    expression -> term { (+|-) term }
    term -> factor { (*|/) factor }
    factor -> id | number | ( expression )
    condition -> expression (=|<>|<|>|<=|>=) expression
    
    为了演示,我们使用更简化的文法:
    S -> E
    E -> E + T | E - T | T
    T -> T * F | T / F | F
    F -> ( E ) | id | num
    """
    grammar = Grammar()
    
    print("创建PL/0简化文法...")
    print("-" * 60)
    
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
    
    print("文法产生式:")
    for i, prod in enumerate(grammar.productions):
        print(f"  {i}: {prod}")
    
    print(f"\n非终结符: {grammar.non_terminals}")
    print(f"终结符: {grammar.terminals}")
    print("-" * 60 + "\n")
    
    return grammar


def demo_lexical_generator():
    """
    演示词法分析生成器
    展示如何将正则表达式转换为DFA
    """
    print("\n" + "="*70)
    print(" 词法分析生成器演示 ".center(70, "="))
    print("="*70 + "\n")
    
    generator = LexicalGenerator()
    
    # 演示1: 识别关键字 "begin"
    print("【演示1】 识别关键字 'begin'")
    print("-" * 70)
    table1, accepting1 = generator.generate("begin", "KEYWORD_BEGIN")
    print("\n生成的DFA转换表:")
    for state in sorted(table1.keys()):
        print(f"  状态 {state}: {table1[state]}")
    print(f"  接受状态: {accepting1}")
    print()
    
    # 演示2: 识别标识符 (简化为字母序列)
    print("\n【演示2】 识别标识符模式")
    print("-" * 70)
    generator2 = LexicalGenerator()
    table2, accepting2 = generator2.generate("abc", "IDENTIFIER")
    print("\n生成的DFA转换表:")
    for state in sorted(table2.keys()):
        print(f"  状态 {state}: {table2[state]}")
    print(f"  接受状态: {accepting2}")
    print()
    
    # 演示3: 识别数字
    print("\n【演示3】 识别数字模式")
    print("-" * 70)
    generator3 = LexicalGenerator()
    table3, accepting3 = generator3.generate("123", "NUMBER")
    print("\n生成的DFA转换表:")
    for state in sorted(table3.keys()):
        print(f"  状态 {state}: {table3[state]}")
    print(f"  接受状态: {accepting3}")
    
    return table1, accepting1


def demo_parser_generator():
    """
    演示语法分析生成器
    展示如何构建LALR(1)分析表
    """
    print("\n" + "="*70)
    print(" 语法分析生成器演示 ".center(70, "="))
    print("="*70 + "\n")
    
    # 创建文法
    grammar = create_pl0_grammar()
    
    # 生成LALR(1)分析表
    print("\n开始生成LALR(1)分析表...")
    print("="*70)
    generator = ParserGenerator(grammar)
    action_table, goto_table = generator.generate()
    
    # 显示FIRST集和FOLLOW集
    print("\n【FIRST集】")
    print("-" * 70)
    for symbol in sorted(generator.first_sets.keys()):
        if symbol in grammar.non_terminals:
            print(f"  FIRST({symbol}) = {generator.first_sets[symbol]}")
    
    print("\n【FOLLOW集】")
    print("-" * 70)
    for symbol in sorted(generator.follow_sets.keys()):
        if symbol in grammar.non_terminals:
            print(f"  FOLLOW({symbol}) = {generator.follow_sets[symbol]}")
    
    # 显示分析表(部分)
    print("\n【ACTION表】(部分显示)")
    print("-" * 70)
    count = 0
    for (state, symbol), (action, value) in sorted(action_table.items()):
        if count < 20:  # 只显示前20条
            print(f"  ACTION[{state:2d}, {symbol:5s}] = {action:6s} {value}")
            count += 1
    if len(action_table) > 20:
        print(f"  ... (共 {len(action_table)} 条)")
    
    print("\n【GOTO表】(部分显示)")
    print("-" * 70)
    count = 0
    for (state, symbol), next_state in sorted(goto_table.items()):
        if count < 15:  # 只显示前15条
            print(f"  GOTO[{state:2d}, {symbol:2s}] = {next_state}")
            count += 1
    if len(goto_table) > 15:
        print(f"  ... (共 {len(goto_table)} 条)")
    
    return grammar, action_table, goto_table


def demo_parser_driver(grammar: Grammar, action_table, goto_table):
    """
    演示LR分析驱动程序
    展示如何使用生成的分析表进行语法分析
    """
    print("\n" + "="*70)
    print(" LR分析驱动程序演示 ".center(70, "="))
    print("="*70 + "\n")
    
    # 创建语义分析器
    semantic_analyzer = PL0SemanticAnalyzer()
    
    # 创建LR分析器,传入语义处理器
    parser = LRParser(
        grammar, 
        action_table, 
        goto_table,
        semantic_handler=semantic_analyzer.semantic_action
    )
    
    # 测试输入: id + id * num
    # 这对应表达式: a + b * 3
    print("【测试输入】 表达式: a + b * 3")
    print("-" * 70)
    print("Token序列: id + id * num")
    print()
    
    tokens = [
        ('id', 'a'),
        ('+', '+'),
        ('id', 'b'),
        ('*', '*'),
        ('num', 3)
    ]
    
    # 执行分析
    success = parser.parse(tokens)
    
    if success:
        print("\n分析结果: [成功]")
        
        # 显示语义分析结果
        semantic_analyzer.print_intermediate_code()
    else:
        print("\n分析结果: [失败]")
    
    return success


def save_tables_to_json(action_table, goto_table, filename="parsing_tables.json"):
    """
    将分析表保存为JSON格式,便于其他程序使用
    """
    print(f"\n保存分析表到 {filename}...")
    
    # 转换为可序列化的格式
    action_dict = {}
    for (state, symbol), (action, value) in action_table.items():
        key = f"({state}, {symbol})"
        action_dict[key] = {"action": action, "value": value}
    
    goto_dict = {}
    for (state, symbol), next_state in goto_table.items():
        key = f"({state}, {symbol})"
        goto_dict[key] = next_state
    
    tables = {
        "action_table": action_dict,
        "goto_table": goto_dict,
        "info": {
            "action_entries": len(action_table),
            "goto_entries": len(goto_table)
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tables, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] 分析表已保存!")


def main():
    """
    主函数: 运行所有演示
    """
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║            编译器生成器 - PL/0语言编译器项目演示                  ║
║                                                                    ║
║  功能模块:                                                         ║
║    1. 词法分析生成器 (RE→NFA→DFA→最小化DFA)                       ║
║    2. 语法分析生成器 (BNF→LR(1)→LALR(1)→分析表)                   ║
║    3. LR分析驱动程序 (基于栈的分析器 + 语义动作接口)              ║
║                                                                    ║
║  作者: 同学A (核心算法引擎负责人)                                 ║
║  接口: 为同学B预留语义分析钩子                                    ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    # 演示1: 词法分析生成器
    demo_lexical_generator()
    
    # 演示2: 语法分析生成器
    grammar, action_table, goto_table = demo_parser_generator()
    
    # 演示3: LR分析驱动程序
    demo_parser_driver(grammar, action_table, goto_table)
    
    # 保存分析表
    save_tables_to_json(action_table, goto_table)
    
    print("\n" + "="*70)
    print(" 演示完成 ".center(70, "="))
    print("="*70)
    print("""
[OK] 所有功能模块演示完成!

文件说明:
  - lexical/  : 词法分析生成器(Thompson构造、子集构造、DFA最小化)
  - syntax/   : 语法分析生成器(FIRST/FOLLOW、LR(1)、LALR(1))
  - driver/   : LR分析驱动程序(语义动作接口)
  - utils/    : 工具函数(日志、文件I/O)
  - main.py   : 主演示程序(本文件)
  - parsing_tables.json : 导出的分析表

给同学B的接口说明:
  详见 API_FOR_TEAMMATE_B.md 文档

答辩演示建议:
  1. 运行此程序展示完整流程
  2. 修改输入表达式展示分析过程
  3. 展示生成的转换表和分析表
  4. 演示语义动作的执行过程
""")


if __name__ == "__main__":
    main()
