#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级测试工具：测试朋友实现的MySemanticAnalyzer
支持完整的类型检查、控制流和回填技术
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
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入必要的类
from lexical import LexicalGenerator, Scanner
from syntax import Grammar, ParserGenerator
from driver import LRParser, ParseTreeVisualizer
from driver.semantic_analyzer_k import MySemanticAnalyzer
from utils.config_loader import ConfigLoader


def test_advanced_file(config_path: str, source_file: str, verbose: bool = True) -> bool:
    """
    使用MySemanticAnalyzer测试源程序文件
    
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
        print(f"[源程序]\n{source_code}")
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
    
    # 创建LRParser，使用MySemanticAnalyzer
    semantic_handler = MySemanticAnalyzer()
    parser = LRParser(grammar, action_table, goto_table, semantic_handler)
    
    try:
        result = parser.parse(tokens)
    except Exception as e:
        print(f"\n[分析错误] {e}")
        import traceback
        traceback.print_exc()
        return False
    
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
        
        # 输出符号表
        if semantic_handler.symbol_table:
            print(f"\n[符号表]")
            for var_name, var_info in semantic_handler.symbol_table.items():
                init_status = "已初始化" if var_info["initialized"] else "未初始化"
                print(f"  {var_name}: {var_info['type']} ({init_status})")
        
        # 输出中间代码
        if semantic_handler.intermediate_code:
            print(f"\n[生成的三地址码] 共{len(semantic_handler.intermediate_code)}条:")
            for idx, code_line in enumerate(semantic_handler.intermediate_code, 1):
                print(f"  {idx:3d}: {code_line}")
            
            # 保存到文件
            from pathlib import Path
            source_name = Path(source_file).stem
            output_dir = "generated"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{source_name}_ir.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for idx, code_line in enumerate(semantic_handler.intermediate_code, 1):
                    f.write(f"{idx:3d}: {code_line}\n")
            
            print(f"\n[已保存] 中间代码已保存至文件: {output_file}")
        
        return True
    else:
        print(f"\n[分析结果] 非法语句(语法错误)")
        return False


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python test_advanced.py <配置文件> <源文件>")
        print("示例: python test_advanced.py configs/grammar_imperative.json test_programs/intermediate_code/advanced_test1.txt")
        sys.exit(1)
    
    config_path = sys.argv[1]
    source_file = sys.argv[2]
    
    if not os.path.exists(config_path):
        print(f"错误: 配置文件不存在 - {config_path}")
        sys.exit(1)
    
    if not os.path.exists(source_file):
        print(f"错误: 源文件不存在 - {source_file}")
        sys.exit(1)
    
    success = test_advanced_file(config_path, source_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
