"""
非确定性有限自动机(NFA)定义
"""

from typing import Set, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from .state import State


@dataclass
class NFA:
    """
    非确定性有限自动机(NFA)
    
    属性:
        states: 所有状态的集合
        alphabet: 输入符号表(不包含epsilon)
        transitions: 状态转换表, 格式: {(state, symbol): {next_states}}
        start_state: 起始状态
        accept_states: 接受状态集合
    """
    states: Set[State] = field(default_factory=set)
    alphabet: Set[str] = field(default_factory=set)
    transitions: Dict[Tuple[State, Optional[str]], Set[State]] = field(
        default_factory=lambda: defaultdict(set)
    )
    start_state: Optional[State] = None
    accept_states: Set[State] = field(default_factory=set)
    
    def add_transition(self, from_state: State, symbol: Optional[str], to_state: State):
        """
        添加状态转换
        
        参数:
            from_state: 源状态
            symbol: 输入符号(None表示epsilon转换)
            to_state: 目标状态
        """
        self.transitions[(from_state, symbol)].add(to_state)
        self.states.add(from_state)
        self.states.add(to_state)
        if symbol is not None:
            self.alphabet.add(symbol)
