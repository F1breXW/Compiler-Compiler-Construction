"""
LR(1)项目定义
"""

from typing import Optional, Tuple
from dataclasses import dataclass
from .grammar import Production


@dataclass(frozen=True)
class LR1Item:
    """
    LR(1)项目
    表示: [A -> α·β, a]
    其中·表示当前分析位置，a是向前看符号(lookahead)
    
    属性:
        production: 所属产生式
        dot_position: 圆点位置(0表示在最左边)
        lookahead: 向前看符号
    """
    production: Production
    dot_position: int
    lookahead: str
    
    def __repr__(self):
        left = self.production.left
        right = list(self.production.right)
        right.insert(self.dot_position, '·')
        return f"[{left} -> {' '.join(right)}, {self.lookahead}]"
    
    def next_symbol(self) -> Optional[str]:
        """
        获取圆点后的符号
        
        返回: 圆点后的符号，如果圆点在末尾则返回None
        """
        if self.dot_position < len(self.production.right):
            return self.production.right[self.dot_position]
        return None
    
    def advance(self) -> 'LR1Item':
        """
        圆点向前移动一位，生成新项目
        
        返回: 新的LR1Item
        """
        return LR1Item(self.production, self.dot_position + 1, self.lookahead)
    
    def core(self) -> Tuple[int, int]:
        """
        返回项目的核心(不包括向前看符号)
        用于LALR(1)合并
        
        返回: (产生式ID, 圆点位置)
        """
        return (self.production.id, self.dot_position)
