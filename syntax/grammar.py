"""
文法和产生式定义
"""

from typing import List, Set, Tuple
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Production:
    """
    产生式类
    表示: left -> right (例如: E -> E + T)
    
    属性:
        id: 产生式唯一标识
        left: 左部非终结符
        right: 右部符号列表
    """
    id: int
    left: str
    right: Tuple[str, ...]  # 使用tuple确保不可变性
    
    def __repr__(self):
        return f"{self.left} -> {' '.join(self.right) if self.right else 'ε'}"


@dataclass
class Grammar:
    """
    上下文无关文法类
    
    属性:
        productions: 产生式列表
        start_symbol: 起始符号
        terminals: 终结符集合
        non_terminals: 非终结符集合
    """
    productions: List[Production] = field(default_factory=list)
    start_symbol: str = "S'"
    terminals: Set[str] = field(default_factory=set)
    non_terminals: Set[str] = field(default_factory=set)
    
    def add_production(self, left: str, right: List[str]):
        """
        添加产生式
        
        参数:
            left: 左部非终结符
            right: 右部符号列表
        """
        prod_id = len(self.productions)
        prod = Production(prod_id, left, tuple(right))
        self.productions.append(prod)
        self.non_terminals.add(left)
        
        # 识别终结符和非终结符 (约定: 大写开头为非终结符)
        for symbol in right:
            if symbol and symbol[0].isupper():
                self.non_terminals.add(symbol)
            elif symbol and symbol != 'ε':
                self.terminals.add(symbol)
    
    def get_productions_by_left(self, left: str) -> List[Production]:
        """
        获取某个非终结符的所有产生式
        
        参数:
            left: 非终结符
        返回: 产生式列表
        """
        return [p for p in self.productions if p.left == left]
    
    def augment(self):
        """
        增广文法: 添加新的起始产生式 S' -> S
        用于LR分析的标准操作
        """
        if self.productions and self.productions[0].left != "S'":
            original_start = self.productions[0].left if self.productions else "S"
            self.productions.insert(0, Production(0, "S'", (original_start,)))
            # 更新所有产生式的ID
            for i, prod in enumerate(self.productions):
                self.productions[i] = Production(i, prod.left, prod.right)
            self.start_symbol = "S'"
            self.non_terminals.add("S'")
