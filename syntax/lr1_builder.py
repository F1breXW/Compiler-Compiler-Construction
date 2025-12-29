"""
LR(1)项目集规范族构建
"""

from typing import Set, FrozenSet, Dict
from collections import deque
from .grammar import Grammar
from .lr_item import LR1Item


class LR1Builder:
    """LR(1)项目集规范族构建器"""
    
    def __init__(self, grammar: Grammar, first_calculator):
        """
        初始化LR(1)构建器
        
        参数:
            grammar: 文法对象
            first_calculator: FIRST集计算器
        """
        self.grammar = grammar
        self.first_calculator = first_calculator
        self.states = []
        self.goto_table = {}
    
    def closure(self, items: Set[LR1Item]) -> FrozenSet[LR1Item]:
        """
        计算LR(1)项目集的闭包
        
        算法原理:
        对于项目 [A -> α·Bβ, a]:
        1. 如果B是非终结符，对于B的每个产生式 B -> γ
        2. 计算FIRST(βa)
        3. 对于FIRST(βa)中的每个终结符b，将项目[B -> ·γ, b]加入闭包
        
        参数:
            items: 初始项目集
        返回: 闭包后的项目集
        """
        closure_set = set(items)
        worklist = list(items)
        
        while worklist:
            item = worklist.pop()
            next_sym = item.next_symbol()
            
            # 如果圆点后是非终结符
            if next_sym and next_sym in self.grammar.non_terminals:
                # 计算βa的FIRST集
                beta = item.production.right[item.dot_position + 1:]  # β
                beta_a = beta + (item.lookahead,)  # βa
                first_beta_a = self.first_calculator.first_of_sequence(beta_a)
                
                # 对于B的每个产生式
                for production in self.grammar.get_productions_by_left(next_sym):
                    # 对于FIRST(βa)中的每个符号
                    for lookahead in first_beta_a:
                        if lookahead != 'ε':
                            new_item = LR1Item(production, 0, lookahead)
                            if new_item not in closure_set:
                                closure_set.add(new_item)
                                worklist.append(new_item)
        
        return frozenset(closure_set)
    
    def goto(self, items: FrozenSet[LR1Item], symbol: str) -> FrozenSet[LR1Item]:
        """
        GOTO函数: 计算项目集在读入某个符号后转移到的项目集
        
        算法原理:
        GOTO(I, X) = CLOSURE({[A -> αX·β, a] | [A -> α·Xβ, a] ∈ I})
        即: 将I中圆点后为X的项目，圆点前移一位，然后求闭包
        
        参数:
            items: 源项目集
            symbol: 输入符号
        返回: GOTO后的项目集
        """
        goto_set = set()
        
        for item in items:
            if item.next_symbol() == symbol:
                goto_set.add(item.advance())
        
        if goto_set:
            return self.closure(goto_set)
        return frozenset()
    
    def build(self):
        """
        构建LR(1)项目集规范族
        
        算法原理:
        1. 初始状态I0 = CLOSURE({[S' -> ·S, $]})
        2. 对于每个未处理的状态I和每个符号X:
           - 计算J = GOTO(I, X)
           - 如果J非空且不在状态集中，加入状态集
           - 记录转移关系: I --X--> J
        3. 重复步骤2，直到没有新状态产生
        """
        print("  [构建LR(1)项目集规范族]")
        
        # 初始项目: [S' -> ·S, $]
        start_production = self.grammar.productions[0]
        start_item = LR1Item(start_production, 0, '$')
        start_state = self.closure({start_item})
        
        self.states = [start_state]
        state_map = {start_state: 0}
        worklist = deque([start_state])
        
        # 收集所有符号
        all_symbols = self.grammar.terminals | self.grammar.non_terminals
        
        while worklist:
            current_state = worklist.popleft()
            current_id = state_map[current_state]
            
            for symbol in all_symbols:
                next_state = self.goto(current_state, symbol)
                
                if next_state:
                    if next_state not in state_map:
                        # 新状态
                        new_id = len(self.states)
                        self.states.append(next_state)
                        state_map[next_state] = new_id
                        worklist.append(next_state)
                    
                    # 记录转移
                    next_id = state_map[next_state]
                    self.goto_table[(current_id, symbol)] = next_id
        
        print(f"    完成! LR(1)状态数: {len(self.states)}")
        
        return self.states, self.goto_table
