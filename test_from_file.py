#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试工具：从文件读取源程序进行词法和语法分析
支持单个文件或批量测试
"""

import sys
import os
import io
from pathlib import Path
from typing import Optional

# Windows控制台编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入必要的类
from lexical import LexicalGenerator, Scanner
from syntax import Grammar, ParserGenerator
from driver import LRParser, PL0SemanticAnalyzer, ParseTreeVisualizer
from utils.config_loader import ConfigLoader, GrammarConfig


def test_file(config_path: str, source_file: str, verbose: bool = True) -> bool:
    """
    测试单个源程序文件
    
    Args:
        config_path: 文法配置文件路径
        source_file: 源程序文件路径
        verbose: 是否输出详细信息
        
    Returns:
        是否通过测试（语法合法）
    """
    # 读取源程序
    with open(source_file, 'r', encoding='utf-8') as f:
        source_code = f.read().strip()
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"[测试文件] {source_file}")
        print(f"[源程序] {source_code}")
        print(f"{'='*70}")
    
    # 加载编译器配置
    loader = ConfigLoader(os.path.dirname(os.path.abspath(config_path)))
    config = loader.load(os.path.basename(config_path))
    
    if verbose:
        print(f"\n使用文法: {config.name}")
    
    # 生成词法分析器
    lexical_gen = LexicalGenerator()
    table, accepting_map = lexical_gen.build(config.lexical_rules)
    lexer = Scanner(table, accepting_map)
    tokens = lexer.scan(source_code)
    
    if verbose:
        print(f"\n[词法分析结果]")
        print(f"  Token序列: {tokens}")
    
    # 生成语法分析器
    grammar = Grammar()
    for rule_str in config.grammar_rules:
        left, right = rule_str.split('->')
        left = left.strip()
        right = [s.strip() for s in right.strip().split()]
        grammar.add_production(left, right)
    
    parser_generator = ParserGenerator(grammar)
    action_table, goto_table = parser_generator.generate()
    
    # 创建LRParser
    parser = LRParser(grammar, action_table, goto_table, PL0SemanticAnalyzer())
    result = parser.parse(tokens)
    
    # 输出分析结果
    if result:
        print(f"\n[分析结果] 合法语句")
        
        # 输出产生式序列
        if parser.production_sequence:
            print(f"\n[产生式序列] 共{len(parser.production_sequence)}步:")
            for idx, prod_idx in enumerate(parser.production_sequence, 1):
                prod = grammar.productions[prod_idx]
                right = ' '.join(prod.right) if prod.right else 'ε'
                print(f"  {idx}. {prod.left} -> {right}")
        
        # 输出语法树
        parse_tree = parser.get_parse_tree()
        if parse_tree:
            print(f"\n[语法树结构]")
            print(ParseTreeVisualizer.to_text(parse_tree))
            
            # 保存语法树文件
            source_name = Path(source_file).stem
            
            # JSON格式
            json_file = f"generated/{source_name}_tree.json"
            os.makedirs("generated", exist_ok=True)
            ParseTreeVisualizer.to_json(parse_tree, json_file)
            print(f"\n[已保存] 语法树: {json_file}")
            
            # DOT格式
            dot_file = f"visualizations/{source_name}_tree.dot"
            if ParseTreeVisualizer.to_dot(parse_tree, dot_file):
                print(f"[已保存] 可视化: {dot_file}")
        
        # 输出中间代码（如果有）
        if hasattr(parser, 'semantic_handler') and parser.semantic_handler:
            if hasattr(parser.semantic_handler, 'code') and parser.semantic_handler.code:
                print(f"\n[生成的中间代码]")
                for idx, code_line in enumerate(parser.semantic_handler.code, 1):
                    print(f"  {idx}: {code_line}")
        
        return True
    else:
        print(f"\n[分析结果] 非法语句(语法错误)")
        return False


def batch_test(config_path: str, test_dir: str, pattern: str = "*.txt"):
    """
    批量测试目录下的所有源程序文件
    
    Args:
        config_path: 文法配置文件路径
        test_dir: 测试文件目录
        pattern: 文件匹配模式
    """
    test_path = Path(test_dir)
    if not test_path.exists():
        print(f"❌ 错误: 目录不存在 - {test_dir}")
        return
    
    # 查找所有测试文件
    test_files = sorted(test_path.glob(pattern))
    
    if not test_files:
        print(f"❌ 错误: 在 {test_dir} 中没有找到匹配 {pattern} 的文件")
        return
    
    print(f"\n{'='*70}")
    print(f"[批量测试模式]")
    print(f"[测试目录] {test_dir}")
    print(f"[测试文件] 找到 {len(test_files)} 个")
    print(f"{'='*70}")
    
    results = []
    for test_file in test_files:
        result = test_file(config_path, str(test_file), verbose=True)
        results.append((test_file.name, result))
        print()  # 空行分隔
    
    # 统计结果
    print(f"\n{'='*70}")
    print(f"[测试总结]")
    print(f"{'='*70}")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for filename, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}  {filename}")
    
    print(f"\n通过率: {passed}/{total} ({100*passed/total:.1f}%)")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="编译器测试工具 - 从文件读取源程序进行词法和语法分析",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 测试单个文件
  python test_from_file.py configs/grammar1_arithmetic.json test_programs/arithmetic_1.txt
  
  # 批量测试目录
  python test_from_file.py configs/grammar1_arithmetic.json test_programs/ --batch
  
  # 简洁模式（只输出结果）
  python test_from_file.py configs/grammar1_arithmetic.json test_programs/arithmetic_1.txt --quiet
        """
    )
    
    parser.add_argument('config', help='文法配置文件路径 (JSON)')
    parser.add_argument('source', help='源程序文件路径或目录')
    parser.add_argument('--batch', '-b', action='store_true', 
                        help='批量测试模式（测试目录下所有.txt文件）')
    parser.add_argument('--pattern', '-p', default='*.txt',
                        help='批量测试时的文件匹配模式（默认: *.txt）')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='简洁模式（减少输出）')
    
    args = parser.parse_args()
    
    # 检查配置文件是否存在
    if not os.path.exists(args.config):
        print(f"❌ 错误: 配置文件不存在 - {args.config}")
        sys.exit(1)
    
    # 执行测试
    if args.batch:
        batch_test(args.config, args.source, args.pattern)
    else:
        result = test_file(args.config, args.source, verbose=not args.quiet)
        sys.exit(0 if result else 1)


if __name__ == '__main__':
    main()
