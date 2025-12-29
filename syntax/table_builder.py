"""
分析表构建器
"""

from typing import List, FrozenSet, Dict, Tuple
from .grammar import Grammar
from .lr_item import LR1Item


class TableBuilder:
    """ACTION表和GOTO表构建器"""
    
    def __init__(self, grammar: Grammar):
        """
        初始化表构建器
        
        参数:
            grammar: 文法对象
        """
        self.grammar = grammar
        self.action_table = {}
        self.goto_table = {}
    
    def build(self, lalr_states: List[FrozenSet[LR1Item]], 
              lalr_goto: Dict[Tuple[int, str], int]):
        """
        构建LALR(1)分析表: ACTION表和GOTO表
        
        ACTION表规则:
        1. 如果[A -> α·aβ, b] ∈ Ii 且 GOTO(Ii, a) = Ij, 则ACTION[i, a] = "shift j"
        2. 如果[A -> α·, a] ∈ Ii 且 A ≠ S', 则ACTION[i, a] = "reduce A->α"
        3. 如果[S' -> S·, $] ∈ Ii, 则ACTION[i, $] = "accept"
        
        GOTO表规则:
        如果GOTO(Ii, A) = Ij, 则GOTO[i, A] = j (A为非终结符)
        
        参数:
            lalr_states: LALR(1)状态列表
            lalr_goto: LALR(1)转移表
        """
        print("  [构建分析表]")
        
        for state_id, state in enumerate(lalr_states):
            for item in state:
                next_sym = item.next_symbol()
                
                if next_sym is not None:
                    # 情况1: [A -> α·aβ, b], a是终结符 -> shift
                    if next_sym in self.grammar.terminals:
                        if (state_id, next_sym) in lalr_goto:
                            next_state = lalr_goto[(state_id, next_sym)]
                            action = ('shift', next_state)
                            
                            # 检查冲突
                            if (state_id, next_sym) in self.action_table:
                                existing = self.action_table[(state_id, next_sym)]
                                if existing != action:
                                    print(f"    [警告] 移进-归约冲突: 状态{state_id}, 符号'{next_sym}'")
                            else:
                                self.action_table[(state_id, next_sym)] = action
                    
                    # GOTO表: A是非终结符
                    elif next_sym in self.grammar.non_terminals:
                        if (state_id, next_sym) in lalr_goto:
                            next_state = lalr_goto[(state_id, next_sym)]
                            self.goto_table[(state_id, next_sym)] = next_state
                
                else:
                    # 情况2: [A -> α·, a] -> reduce
                    production = item.production
                    lookahead = item.lookahead
                    
                    if production.left == "S'" and lookahead == '$':
                        # 情况3: accept
                        self.action_table[(state_id, '$')] = ('accept', 0)
                    else:
                        action = ('reduce', production.id)
                        
                        # 检查冲突
                        if (state_id, lookahead) in self.action_table:
                            existing = self.action_table[(state_id, lookahead)]
                            if existing != action:
                                print(f"    [警告] 归约-归约冲突: 状态{state_id}, 向前看'{lookahead}'")
                        else:
                            self.action_table[(state_id, lookahead)] = action
        
        print(f"    完成! ACTION表项: {len(self.action_table)}, GOTO表项: {len(self.goto_table)}")
        
        return self.action_table, self.goto_table
