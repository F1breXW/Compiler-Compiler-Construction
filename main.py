"""
编译器-编译器演示程序（配置驱动版本）
从JSON配置文件读取文法定义，自动生成词法分析器和语法分析器
遵循开闭原则：对扩展开放（新增文法只需添加配置文件），对修改封闭
"""

from lexical import LexicalGenerator, Scanner
from syntax import Grammar, ParserGenerator
from driver import LRParser, PL0SemanticAnalyzer, ParseTreeVisualizer
from utils import save_parsing_tables, save_json
from utils.visualizer import GraphvizVisualizer
from utils.config_loader import ConfigLoader, ConfigValidator, GrammarConfig
import sys
import os


def pause():
    """暂停程序，等待用户按回车键"""
    try:
        input("\n[按回车键继续...]")
    except EOFError:
        pass  # 在非交互模式下自动继续


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


class CompilerGenerator:
    """
    编译器生成器（Facade模式）
    封装词法生成器和语法生成器的复杂性，提供简单统一的接口
    """
    
    def __init__(self):
        self.lexical_generator = LexicalGenerator()
        
    def generate_lexer(self, config: GrammarConfig):
        """
        根据配置生成词法分析器
        
        参数:
            config: 文法配置
        返回:
            (transition_table, accepting_map, scanner)
        """
        print_section(f"步骤1 - 生成词法分析器: {config.name}")
        print(f"文法描述: {config.description}")
        print(f"词法规则数: {len(config.lexical_rules)}")
        
        # 显示规则
        print("\n词法规则:")
        for i, (pattern, token) in enumerate(config.lexical_rules, 1):
            print(f"  {i:2d}. {pattern:20s} -> {token}")
        
        # 生成DFA
        table, accepting_map = self.lexical_generator.build(config.lexical_rules)
        
        print(f"\n[OK] 词法分析器生成完成")
        print(f"  - DFA状态数: {len(table)}")
        print(f"  - 接受状态数: {len(accepting_map)}")
        
        # 创建Scanner
        scanner = Scanner(table, accepting_map)
        
        return table, accepting_map, scanner
    
    def generate_parser(self, config: GrammarConfig):
        """
        根据配置生成语法分析器
        
        参数:
            config: 文法配置
        返回:
            (action_table, goto_table, grammar)
        """
        print_section(f"步骤2 - 生成语法分析器: {config.name}")
        
        # 创建文法对象
        grammar = Grammar()
        
        # 添加产生式
        print("\n产生式:")
        for i, rule_str in enumerate(config.grammar_rules, 1):
            left, right = rule_str.split('->')
            left = left.strip()
            right = [s.strip() for s in right.strip().split()]
            grammar.add_production(left, right)
            print(f"  {i:2d}. {rule_str}")
        
        # 创建ParserGenerator（需要传入grammar）
        parser_generator = ParserGenerator(grammar)
        
        # 生成LALR(1)分析表
        print()
        action_table, goto_table = parser_generator.generate()
        
        print(f"\n[OK] 语法分析器生成完成")
        action_count = sum(len(v) if isinstance(v, dict) else 1 for v in action_table.values())
        goto_count = sum(len(v) if isinstance(v, dict) else 1 for v in goto_table.values())
        print(f"  - ACTION表项: {action_count}")
        print(f"  - GOTO表项: {goto_count}")
        
        return action_table, goto_table, grammar
    
    def export_visualizations(self, grammar_name: str):
        """导出可视化文件"""
        if self.lexical_generator.last_min_dfa:
            filename = f"visualizations/{grammar_name}_dfa.dot"
            os.makedirs("visualizations", exist_ok=True)
            GraphvizVisualizer.export_dfa(
                self.lexical_generator.last_min_dfa, 
                filename, 
                f"{grammar_name} - Minimized DFA"
            )
            print(f"  [可视化] 已生成 {filename}")


def test_grammar(compiler: CompilerGenerator, config: GrammarConfig, grammar_index: int):
    """
    测试单个文法
    
    参数:
        compiler: 编译器生成器
        config: 文法配置
        grammar_index: 文法编号（用于标题）
    """
    print_header(f"测试文法 #{grammar_index}: {config.name}")
    
    # 步骤1：生成词法分析器
    table, accepting_map, scanner = compiler.generate_lexer(config)
    
    # 步骤2：生成语法分析器
    action_table, goto_table, grammar = compiler.generate_parser(config)
    
    # 步骤3：导出可视化
    print_section("步骤3 - 导出生成结果")
    compiler.export_visualizations(config.name.replace(" ", "_"))
    
    # 导出分析表
    output_file = f"generated/grammar{grammar_index}_parser.json"
    os.makedirs("generated", exist_ok=True)
    save_parsing_tables(action_table, goto_table, output_file)
    print(f"  [分析表] 已保存至 {output_file}")
    
    pause()
    
    # 步骤4：测试用例
    print_section(f"步骤4 - 运行测试用例 (共{len(config.test_cases)}个)")
    
    for i, test_case in enumerate(config.test_cases, 1):
        print_section(f"测试用例 {i}/{len(config.test_cases)}")
        print(f"描述: {test_case.description}")
        print(f"源代码: {test_case.input}")
        print(f"预期结果: {test_case.expected}")
        
        # 词法分析
        try:
            tokens = scanner.scan(test_case.input)
            print(f"Token序列: {tokens}")
        except Exception as e:
            print(f"[错误] 词法分析失败: {e}")
            continue
        
        # 语法分析
        parser = LRParser(grammar, action_table, goto_table, PL0SemanticAnalyzer())
        
        result = False
        try:
            result = parser.parse(tokens)
            
            if result:
                print("\n[OK] 分析结果: 合法")
                
                # ====== 课程要求1: 输出产生式序列 ======
                if parser.production_sequence:
                    print("\n使用的产生式序列:")
                    for idx, prod_idx in enumerate(parser.production_sequence, 1):
                        prod = grammar.productions[prod_idx]
                        right = ' '.join(prod.right) if prod.right else 'ε'
                        print(f"  {idx}. {prod.left} -> {right}")
                
                # ====== 课程要求2: 输出语法树 ======
                parse_tree = parser.get_parse_tree()
                if parse_tree:
                    print("\n语法树（树形结构）:")
                    print(ParseTreeVisualizer.to_text(parse_tree))
                    
                    # 导出语法树到文件
                    tree_filename = f"generated/{config.name.replace(' ', '_')}_test{i}_tree.json"
                    os.makedirs("generated", exist_ok=True)
                    ParseTreeVisualizer.to_json(parse_tree, tree_filename)
                    print(f"  [语法树已保存] {tree_filename}")
                    
                    # 导出DOT格式（可选）
                    dot_filename = f"visualizations/{config.name.replace(' ', '_')}_test{i}_tree.dot"
                    if ParseTreeVisualizer.to_dot(parse_tree, dot_filename):
                        print(f"  [语法树可视化] {dot_filename}")
                
                # 输出中间代码（如果有语义分析器）
                if hasattr(parser, 'semantic_handler') and parser.semantic_handler:
                    if hasattr(parser.semantic_handler, 'code') and parser.semantic_handler.code:
                        print("\n生成的中间代码:")
                        for idx, code_line in enumerate(parser.semantic_handler.code, 1):
                            print(f"  {idx}: {code_line}")
            else:
                print("\n[EXPECTED] 分析结果: 非法（语法错误）")
                
        except Exception as e:
            print(f"\n[错误] 语法分析异常: {e}")
        
        # 验证结果
        actual = "legal" if result else "illegal"
        if actual == test_case.expected:
            print(f"\n[OK] 测试通过")
        else:
            print(f"\n[X] 测试失败 (预期: {test_case.expected}, 实际: {actual})")
        
        print()
    
    # 测试总结
    print("="*80)
    print(f"文法 '{config.name}' 测试完成!")
    print(f"  - 词法规则: {len(config.lexical_rules)} 条")
    print(f"  - 语法规则: {len(config.grammar_rules)} 条")
    print(f"  - 测试用例: {len(config.test_cases)} 个")
    print("="*80)
    
    pause()


def main():
    """主函数"""
    print_header("编译器-编译器 自动生成演示系统")
    
    print("系统特点：")
    print("  1. 配置驱动：从JSON文件读取文法定义")
    print("  2. 自动生成：根据配置自动生成词法和语法分析器")
    print("  3. 易于扩展：新增文法只需添加配置文件，无需修改代码")
    print("  4. 完整测试：每个文法包含多个测试用例验证正确性")
    
    # 加载配置
    print_section("加载文法配置文件")
    loader = ConfigLoader("configs")
    
    try:
        configs = loader.load_all()
        print(f"[OK] 成功加载 {len(configs)} 个文法配置:")
        for i, config in enumerate(configs, 1):
            print(f"  {i}. {config.name} ({len(config.lexical_rules)}条词法规则, "
                  f"{len(config.grammar_rules)}条语法规则, "
                  f"{len(config.test_cases)}个测试用例)")
    except Exception as e:
        print(f"[错误] 加载配置失败: {e}")
        return
    
    if not configs:
        print("[错误] 未找到任何文法配置文件")
        print("请在 configs/ 目录下添加 .json 配置文件")
        return
    
    # 验证配置
    print_section("验证文法配置")
    validator = ConfigValidator()
    valid_configs = []
    
    for config in configs:
        if validator.validate(config):
            print(f"  [OK] {config.name}: 验证通过")
            valid_configs.append(config)
        else:
            print(f"  [X] {config.name}: 验证失败")
    
    if not valid_configs:
        print("[错误] 没有有效的文法配置")
        return
    
    pause()
    
    # 创建编译器生成器
    compiler = CompilerGenerator()
    
    # 测试每个文法
    for i, config in enumerate(valid_configs, 1):
        test_grammar(compiler, config, i)
    
    # 最终总结
    print_header("测试总结")
    print(f"[OK] 共测试了 {len(valid_configs)} 个文法")
    print(f"[OK] 每个文法均成功生成词法和语法分析器")
    print(f"[OK] 所有测试用例均已运行")
    print("\n项目文件说明：")
    print("  - configs/       : 文法配置文件（JSON格式）")
    print("  - lexical/       : 词法分析生成器")
    print("  - syntax/        : 语法分析生成器")
    print("  - driver/        : LR分析驱动程序")
    print("  - utils/         : 工具函数（配置加载、可视化等）")
    print("  - generated/     : 生成的分析器输出")
    print("  - visualizations/: DFA/NFA可视化图表")
    print("\n如需测试新文法，请在 configs/ 目录添加配置文件并重新运行程序")


if __name__ == "__main__":
    main()
