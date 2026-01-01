#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
中间代码生成测试工具
测试语义分析器生成三地址码的能力
"""

import sys
import os
import io
from pathlib import Path

# Windows控制台编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from lexical import LexicalGenerator, Scanner
from syntax import Grammar, ParserGenerator
from driver import LRParser
from driver.semantic_analyzer_k import MySemanticAnalyzer
from utils.config_loader import ConfigLoader


def test_intermediate_code(config_path: str, source_file: str):
    """
    测试中间代码生成
    
    Args:
        config_path: 文法配置文件路径
        source_file: 源程序文件路径
    """
    print(f"\n{'='*70}")
    print(f"[测试文件] {source_file}")
    print(f"{'='*70}")
    
    # 读取源程序
    with open(source_file, 'r', encoding='utf-8') as f:
        source_code = f.read().strip()
    
    print(f"\n[源程序]")
    print(source_code)
    print(f"\n{'-'*70}")
    
    # 加载配置
    loader = ConfigLoader(os.path.dirname(os.path.abspath(config_path)))
    config = loader.load(os.path.basename(config_path))
    
    print(f"\n[使用文法] {config.name}")
    
    # 生成词法分析器
    lexical_gen = LexicalGenerator()
    table, accepting_map = lexical_gen.build(config.lexical_rules)
    lexer = Scanner(table, accepting_map)
    
    # 词法分析
    tokens = lexer.scan(source_code)
    print(f"\n[词法分析] Token序列:")
    print(f"  {tokens}")
    
    # 生成语法分析器
    grammar = Grammar()
    for rule_str in config.grammar_rules:
        left, right = rule_str.split('->')
        left = left.strip()
        right = [s.strip() for s in right.strip().split()]
        grammar.add_production(left, right)
    
    parser_generator = ParserGenerator(grammar)
    action_table, goto_table = parser_generator.generate()
    
    # 创建语义分析器
    semantic_analyzer = MySemanticAnalyzer()
    
    # 创建LR分析器
    parser = LRParser(grammar, action_table, goto_table, semantic_analyzer)
    
    # 执行分析
    print(f"\n{'-'*70}")
    print("[语法分析和语义分析]")
    print(f"{'-'*70}")
    
    try:
        result = parser.parse(tokens)
        
        if result:
            print(f"\n{'='*70}")
            print("[分析结果] 源程序合法")
            print(f"{'='*70}")
            
            # 输出符号表
            if semantic_analyzer.symbol_table:
                print(f"\n[符号表]")
                for var_name, var_info in semantic_analyzer.symbol_table.items():
                    if isinstance(var_info, dict):
                        print(f"  {var_name}: type={var_info.get('type', '?')}, "
                              f"initialized={var_info.get('initialized', False)}")
                    else:
                        print(f"  {var_name}: {var_info}")
            
            # 输出中间代码
            if semantic_analyzer.intermediate_code:
                print(f"\n[生成的三地址码] 共{len(semantic_analyzer.intermediate_code)}条指令")
                print(f"{'-'*70}")
                for idx, code in enumerate(semantic_analyzer.intermediate_code, 1):
                    print(f"  {idx:3d}: {code}")
                print(f"{'-'*70}")
                
                # 保存到文件
                source_name = Path(source_file).stem
                output_file = f"generated/{source_name}_ir.txt"
                os.makedirs("generated", exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    for idx, code in enumerate(semantic_analyzer.intermediate_code, 1):
                        f.write(f"{idx:3d}: {code}\n")
                
                print(f"\n[已保存] 中间代码文件: {output_file}")
            else:
                print(f"\n[提示] 未生成中间代码")
            
            return True
        else:
            print(f"\n{'='*70}")
            print("[分析结果] 源程序存在语法错误")
            print(f"{'='*70}")
            return False
            
    except Exception as e:
        print(f"\n[错误] 分析异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="中间代码生成测试工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 测试单个文件
  python test_intermediate_code.py configs/grammar_imperative.json test_programs/intermediate_code/test1_arithmetic.txt
  
  # 批量测试
  python test_intermediate_code.py configs/grammar_imperative.json test_programs/intermediate_code/ --batch
        """
    )
    
    parser.add_argument('config', help='文法配置文件路径')
    parser.add_argument('source', help='源程序文件路径或目录')
    parser.add_argument('--batch', '-b', action='store_true', 
                        help='批量测试模式')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.config):
        print(f"[错误] 配置文件不存在: {args.config}")
        sys.exit(1)
    
    if args.batch:
        # 批量测试
        test_dir = Path(args.source)
        if not test_dir.exists():
            print(f"[错误] 目录不存在: {args.source}")
            sys.exit(1)
        
        test_files = sorted(test_dir.glob("*.txt"))
        if not test_files:
            print(f"[错误] 在 {args.source} 中没有找到.txt文件")
            sys.exit(1)
        
        print(f"\n{'='*70}")
        print(f"[批量测试模式] 找到 {len(test_files)} 个测试文件")
        print(f"{'='*70}")
        
        results = []
        for test_file in test_files:
            result = test_intermediate_code(args.config, str(test_file))
            results.append((test_file.name, result))
            print("\n")
        
        # 统计结果
        print(f"\n{'='*70}")
        print(f"[测试总结]")
        print(f"{'='*70}")
        passed = sum(1 for _, r in results if r)
        total = len(results)
        
        for filename, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"  {status}  {filename}")
        
        print(f"\n通过率: {passed}/{total} ({100*passed/total:.1f}%)")
    else:
        # 单个测试
        result = test_intermediate_code(args.config, args.source)
        sys.exit(0 if result else 1)


if __name__ == '__main__':
    main()
