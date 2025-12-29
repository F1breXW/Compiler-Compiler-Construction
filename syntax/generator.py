"""
语法分析生成器主类
"""

from typing import Tuple, Dict
from .grammar import Grammar
from .first_follow import FirstFollowCalculator
from .lr1_builder import LR1Builder
from .lalr_builder import LALRBuilder
from .table_builder import TableBuilder


class ParserGenerator:
    """
    语法分析生成器
    负责从BNF文法生成LALR(1)分析表
    """
    
    def __init__(self, grammar: Grammar):
        """
        初始化语法生成器
        
        参数:
            grammar: 输入的上下文无关文法
        """
        self.grammar = grammar
        self.grammar.augment()  # 增广文法
        self.grammar.terminals.add('$')  # 添加结束标记
        
        # 初始化各个组件
        self.first_follow_calc = FirstFollowCalculator(grammar)
        self.lr1_builder = None
        self.table_builder = TableBuilder(grammar)
        
        # 结果存储
        self.first_sets = {}
        self.follow_sets = {}
        self.action_table = {}
        self.goto_table = {}
    
    def generate(self) -> Tuple[Dict, Dict]:
        """
        主接口: 生成LALR(1)分析表
        
        返回: (action_table, goto_table)
            - action_table: {(state, terminal): (action, value)}
            - goto_table: {(state, non_terminal): next_state}
        """
        print("[语法生成器] 开始构建LALR(1)分析表")
        
        # 步骤1: 计算FIRST和FOLLOW集
        print("\n[步骤1] 计算FIRST和FOLLOW集")
        self.first_follow_calc.compute_first_sets()
        self.first_follow_calc.compute_follow_sets()
        self.first_sets = self.first_follow_calc.first_sets
        self.follow_sets = self.first_follow_calc.follow_sets
        
        # 步骤2: 构建LR(1)项目集规范族
        print("\n[步骤2] 构建LR(1)项目集")
        self.lr1_builder = LR1Builder(self.grammar, self.first_follow_calc)
        lr1_states, lr1_goto = self.lr1_builder.build()
        
        # 步骤3: 合并为LALR(1)
        print("\n[步骤3] 压缩为LALR(1)")
        lalr_states, lalr_goto = LALRBuilder.merge(lr1_states, lr1_goto)
        
        # 步骤4: 构建分析表
        print("\n[步骤4] 生成分析表")
        self.action_table, self.goto_table = self.table_builder.build(
            lalr_states, lalr_goto
        )
        
        print("\n[语法生成器] 完成!\n")
        
        return self.action_table, self.goto_table
