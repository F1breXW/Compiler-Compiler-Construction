"""
状态类定义
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class State:
    """
    有限自动机的状态类
    
    属性:
        id: 状态的唯一标识符
        is_accepting: 是否为接受状态
        tag: 接受状态的标签(如果是接受状态，表示识别的token类型)
    """
    id: int
    is_accepting: bool = False
    tag: Optional[str] = None
    priority: int = float('inf')
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, State) and self.id == other.id
    
    def __repr__(self):
        return f"State({self.id}, accept={self.is_accepting})"
