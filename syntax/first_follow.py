"""
FIRST集和FOLLOW集计算
"""

from typing import Set, Dict, Tuple
from .grammar import Grammar


class FirstFollowCalculator:
    """FIRST集和FOLLOW集计算器"""
    
    def __init__(self, grammar: Grammar):
        """
        初始化计算器
        
        参数:
            grammar: 文法对象
        """
        self.grammar = grammar
        self.first_sets: Dict[str, Set[str]] = {}
        self.follow_sets: Dict[str, Set[str]] = {}
    
    def compute_first_sets(self):
        """
        计算所有符号的FIRST集
        
        算法原理:
        1. 对于终结符a: FIRST(a) = {a}
        2. 对于非终结符A:
           - 如果有产生式 A -> ε, 则 ε ∈ FIRST(A)
           - 如果有产生式 A -> X1X2...Xn:
             * 将FIRST(X1)-{ε} 加入FIRST(A)
             * 如果ε ∈ FIRST(Xi) (i=1...k-1), 将FIRST(Xk)-{ε} 加入FIRST(A)
             * 如果ε ∈ FIRST(Xi) (i=1...n), 将ε加入FIRST(A)
        3. 重复应用规则2，直到所有FIRST集不再变化
        """
        print("  [计算FIRST集]")
        
        # 初始化: 终结符的FIRST集
        for terminal in self.grammar.terminals:
            self.first_sets[terminal] = {terminal}
        
        # 初始化: 非终结符的FIRST集为空
        for non_terminal in self.grammar.non_terminals:
            self.first_sets[non_terminal] = set()
        
        # 迭代计算直到不动点
        changed = True
        while changed:
            changed = False
            
            for production in self.grammar.productions:
                left = production.left
                right = production.right
                
                if not right or right == ('ε',):
                    # A -> ε
                    if 'ε' not in self.first_sets[left]:
                        self.first_sets[left].add('ε')
                        changed = True
                else:
                    # A -> X1 X2 ... Xn
                    for symbol in right:
                        # 获取当前符号的FIRST集
                        if symbol in self.first_sets:
                            symbol_first = self.first_sets[symbol]
                        else:
                            # 如果是未知符号，假设为终结符
                            symbol_first = {symbol}
                            self.first_sets[symbol] = symbol_first
                        
                        # 将FIRST(symbol) - {ε} 加入FIRST(left)
                        before_size = len(self.first_sets[left])
                        self.first_sets[left] |= (symbol_first - {'ε'})
                        if len(self.first_sets[left]) > before_size:
                            changed = True
                        
                        # 如果ε不在FIRST(symbol)中，停止
                        if 'ε' not in symbol_first:
                            break
                    else:
                        # 所有符号都能推出ε
                        if 'ε' not in self.first_sets[left]:
                            self.first_sets[left].add('ε')
                            changed = True
        
        print(f"    完成! 共计算{len(self.first_sets)}个符号的FIRST集")
    
    def compute_follow_sets(self):
        """
        计算所有非终结符的FOLLOW集
        
        算法原理:
        1. 将$加入FOLLOW(S), S为起始符号
        2. 如果有产生式 A -> αBβ:
           - 将FIRST(β)-{ε} 加入FOLLOW(B)
           - 如果ε ∈ FIRST(β), 将FOLLOW(A)加入FOLLOW(B)
        3. 如果有产生式 A -> αB:
           - 将FOLLOW(A)加入FOLLOW(B)
        4. 重复应用规则2和3，直到所有FOLLOW集不再变化
        """
        print("  [计算FOLLOW集]")
        
        # 初始化
        for non_terminal in self.grammar.non_terminals:
            self.follow_sets[non_terminal] = set()
        
        # 起始符号的FOLLOW集包含$
        self.follow_sets[self.grammar.start_symbol].add('$')
        
        # 迭代计算直到不动点
        changed = True
        while changed:
            changed = False
            
            for production in self.grammar.productions:
                left = production.left
                right = production.right
                
                for i, symbol in enumerate(right):
                    if symbol in self.grammar.non_terminals:
                        # 找到非终结符B
                        beta = right[i+1:]  # B后面的符号序列
                        
                        if beta:
                            # 情况1: A -> αBβ
                            # 计算FIRST(β)
                            first_beta = self.first_of_sequence(beta)
                            
                            # 将FIRST(β)-{ε} 加入FOLLOW(B)
                            before_size = len(self.follow_sets[symbol])
                            self.follow_sets[symbol] |= (first_beta - {'ε'})
                            if len(self.follow_sets[symbol]) > before_size:
                                changed = True
                            
                            # 如果ε ∈ FIRST(β), 将FOLLOW(A)加入FOLLOW(B)
                            if 'ε' in first_beta:
                                before_size = len(self.follow_sets[symbol])
                                self.follow_sets[symbol] |= self.follow_sets[left]
                                if len(self.follow_sets[symbol]) > before_size:
                                    changed = True
                        else:
                            # 情况2: A -> αB
                            before_size = len(self.follow_sets[symbol])
                            self.follow_sets[symbol] |= self.follow_sets[left]
                            if len(self.follow_sets[symbol]) > before_size:
                                changed = True
        
        print(f"    完成! 共计算{len(self.follow_sets)}个非终结符的FOLLOW集")
    
    def first_of_sequence(self, sequence: Tuple[str, ...]) -> Set[str]:
        """
        计算符号序列的FIRST集
        
        参数:
            sequence: 符号序列
        返回: FIRST集
        """
        result = set()
        for symbol in sequence:
            if symbol in self.first_sets:
                symbol_first = self.first_sets[symbol]
            else:
                symbol_first = {symbol}
            
            result |= (symbol_first - {'ε'})
            
            if 'ε' not in symbol_first:
                break
        else:
            # 所有符号都能推出ε
            result.add('ε')
        
        return result
