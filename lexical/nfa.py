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
    
    def __post_init__(self):
        # 确保transitions是一个defaultdict，即使反序列化时也一样
        if not isinstance(self.transitions, defaultdict):
            # 如果不是defaultdict，创建一个新的defaultdict并复制数据
            old_transitions = self.transitions
            self.transitions = defaultdict(set)
            self.transitions.update(old_transitions)

    def add_transition(self, from_state: State, symbol: Optional[str], to_state: State):
        """
        添加状态转换
        
        参数:
            from_state: 源状态
            symbol: 输入符号(None表示epsilon转换)
            to_state: 目标状态
        """
        # 确保key存在
        key = (from_state, symbol)
        if key not in self.transitions:
            self.transitions[key] = set()
            
        self.transitions[key].add(to_state)
        self.states.add(from_state)
        self.states.add(to_state)
        if symbol is not None:
            self.alphabet.add(symbol)
