#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
演示脚本：分步骤展示编译器生成过程
阶段1：输入文法 → 生成词法分析器和语法分析器
阶段2：输入源程序 → 输出分析结果
"""

import sys
import os
import io
from pathlib import Path

# Windows控制台编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from lexical import LexicalGenerator, Scanner
from syntax import Grammar, ParserGenerator
from driver import LRParser, PL0SemanticAnalyzer, ParseTreeVisualizer
from utils.config_loader import ConfigLoader
from utils.visualizer import GraphvizVisualizer
from visualize_table import generate_table_html


def stage1_generate_compiler(config_path: str):
    """
    阶段1：输入文法规则，自动生成词法分析器和语法分析器
    
    Args:
        config_path: 文法配置文件路径
        
    Returns:
        (lexer, grammar, action_table, goto_table) - 生成的编译器组件
    """
    print("=" * 80)
    print("【阶段1】输入文法规则 → 自动生成词法分析器和语法分析器")
    print("=" * 80)
    
    # 加载编译器配置
    loader = ConfigLoader(os.path.dirname(os.path.abspath(config_path)))
    config = loader.load(os.path.basename(config_path))
    
    print(f"\n[输入] 文法配置文件: {config_path}")
    print(f"[文法名称] {config.name}")
    
    # ===== 第1步：生成词法分析器 =====
    print("\n" + "-" * 80)
    print("【步骤1】生成词法分析器")
    print("-" * 80)
    
    lexical_gen = LexicalGenerator()
    table, accepting_map = lexical_gen.build(config.lexical_rules)
    lexer = Scanner(table, accepting_map)
    
    print(f"\n✅ 词法分析器生成完成！")
    print(f"   - 词法规则数: {len(config.lexical_rules)}")
    print(f"   - DFA状态数: {len(table)}")
    print(f"   - 识别Token类型: {list(accepting_map.values())}")
    
    # 可视化DFA
    if lexical_gen.last_min_dfa:
        os.makedirs("visualizations", exist_ok=True)
        dot_file = f"visualizations/{config.name.replace(' ', '_')}_dfa.dot"
        GraphvizVisualizer.export_dfa(lexical_gen.last_min_dfa, dot_file)
        print(f"   - [可视化] DFA已导出: {dot_file}")

    # ===== 第2步：生成语法分析器 =====
    print("\n" + "-" * 80)
    print("【步骤2】生成语法分析器（LALR(1)）")
    print("-" * 80)
    
    grammar = Grammar()
    for rule_str in config.grammar_rules:
        left, right = rule_str.split('->')
        left = left.strip()
        right = [s.strip() for s in right.strip().split()]
        grammar.add_production(left, right)
    
    print(f"\n[文法规则] 共{len(grammar.productions)}个产生式:")
    for idx, prod in enumerate(grammar.productions):
        right = ' '.join(prod.right) if prod.right else 'ε'
        print(f"  {idx + 1}. {prod.left} -> {right}")
    
    parser_generator = ParserGenerator(grammar)
    action_table, goto_table = parser_generator.generate()
    
    # 计算状态数
    states = set()
    for state, _ in action_table.keys():
        states.add(state)
    for state, _ in goto_table.keys():
        states.add(state)
    # 确保包含状态0（初始状态），即使它没有任何动作（虽然不太可能）
    states.add(0)
    
    print(f"\n✅ 语法分析器生成完成！")
    print(f"   - LALR(1)状态数: {len(states)}")
    print(f"   - ACTION表项数: {len(action_table)}")
    print(f"   - GOTO表项数: {len(goto_table)}")
    
    # 可视化分析表
    html_file = f"visualizations/{config.name.replace(' ', '_')}_lalr_table.html"
    generate_table_html(config_path, html_file, action_table, goto_table)
    print(f"   - [可视化] LALR分析表已导出: {html_file}")

    print("\n" + "=" * 80)
    print("【阶段1完成】编译器已自动生成！")
    print("=" * 80)
    
    return lexer, grammar, action_table, goto_table


def stage2_test_parser(lexer, grammar, action_table, goto_table, source_file: str):
    """
    阶段2：输入源程序，输出分析结果
    
    Args:
        lexer: 词法分析器
        grammar: 文法对象
        action_table: ACTION表
        goto_table: GOTO表
        source_file: 源程序文件路径
        
    Returns:
        bool - 是否为合法语句
    """
    print("\n\n")
    print("=" * 80)
    print("【阶段2】输入源程序 → 输出分析结果")
    print("=" * 80)
    
    # 读取源程序
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read().strip()
    except UnicodeDecodeError:
        try:
            # 尝试GBK编码（Windows默认）
            with open(source_file, 'r', encoding='gbk') as f:
                source_code = f.read().strip()
        except UnicodeDecodeError:
            # 尝试UTF-16（PowerShell默认）
            with open(source_file, 'r', encoding='utf-16') as f:
                source_code = f.read().strip()
    
    print(f"\n[输入] 源程序文件: {source_file}")
    print(f"[源代码] {source_code}")
    
    # ===== 第1步：词法分析 =====
    print("\n" + "-" * 80)
    print("【步骤1】词法分析")
    print("-" * 80)
    
    tokens = lexer.scan(source_code)
    print(f"\n✅ Token序列: {tokens}")
    
    # ===== 第2步：语法分析 =====
    print("\n" + "-" * 80)
    print("【步骤2】语法分析（LR分析过程见上方）")
    print("-" * 80)
    
    parser = LRParser(grammar, action_table, goto_table, PL0SemanticAnalyzer())
    result = parser.parse(tokens)
    
    # ===== 输出结果 =====
    print("\n" + "=" * 80)
    print("【阶段2完成】分析结果")
    print("=" * 80)
    
    if result:
        print(f"\n✅ 【输出1】合法性判断: 合法语句")
        
        # 输出产生式序列
        if parser.production_sequence:
            print(f"\n✅ 【输出2】产生式序列（共{len(parser.production_sequence)}步）:")
            for idx, prod_idx in enumerate(parser.production_sequence, 1):
                prod = grammar.productions[prod_idx]
                right = ' '.join(prod.right) if prod.right else 'ε'
                print(f"  {idx}. {prod.left} -> {right}")
        
        # 输出语法树
        parse_tree = parser.get_parse_tree()
        if parse_tree:
            print(f"\n✅ 【输出3】语法树结构:")
            print(ParseTreeVisualizer.to_text(parse_tree))
            
            # 保存语法树文件
            source_name = Path(source_file).stem
            json_file = f"generated/{source_name}_tree.json"
            os.makedirs("generated", exist_ok=True)
            ParseTreeVisualizer.to_json(parse_tree, json_file)
            print(f"\n[已保存] 语法树JSON: {json_file}")
            
            dot_file = f"visualizations/{source_name}_tree.dot"
            if ParseTreeVisualizer.to_dot(parse_tree, dot_file):
                print(f"[已保存] 语法树DOT: {dot_file}")
        
        return True
    else:
        print(f"\n❌ 【输出1】合法性判断: 非法语句（语法错误）")
        return False


def main():
    """主函数：完整演示流程"""
    if len(sys.argv) < 3:
        print("用法: python demo_two_stages.py <文法配置文件> <源程序文件>")
        print("\n示例:")
        print("  python demo_two_stages.py configs/grammar1_arithmetic.json test_programs/arithmetic_1.txt")
        sys.exit(1)
    
    config_path = sys.argv[1]
    source_file = sys.argv[2]
    
    # 检查文件是否存在
    if not os.path.exists(config_path):
        print(f"❌ 错误: 文法配置文件不存在 - {config_path}")
        sys.exit(1)
    
    if not os.path.exists(source_file):
        print(f"❌ 错误: 源程序文件不存在 - {source_file}")
        sys.exit(1)
    
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "   编译器生成器演示：分步骤展示".center(76) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    # 阶段1：生成编译器
    lexer, grammar, action_table, goto_table = stage1_generate_compiler(config_path)
    
    # 暂停，等待用户确认
    print("\n" + "▶" * 40)
    input("【按回车键继续到阶段2】")
    print("▶" * 40)
    
    # 阶段2：测试源程序
    stage2_test_parser(lexer, grammar, action_table, goto_table, source_file)
    
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "   演示完成！".center(76) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80 + "\n")


if __name__ == "__main__":
    main()
