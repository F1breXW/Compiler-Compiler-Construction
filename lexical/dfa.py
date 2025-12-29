"""
确定性有限自动机(DFA)定义
"""

from typing import Set, Dict, Tuple
from dataclasses import dataclass, field


@dataclass
class DFA:
    """
    确定性有限自动机(DFA)
    
    属性:
        states: 所有状态的集合
        alphabet: 输入符号表
        transitions: 状态转换表, 格式: {(state, symbol): next_state}
        start_state: 起始状态
        accept_states: 接受状态集合
    """
    states: Set[int] = field(default_factory=set)
    alphabet: Set[str] = field(default_factory=set)
    transitions: Dict[Tuple[int, str], int] = field(default_factory=dict)
    start_state: int = 0
    accept_states: Set[int] = field(default_factory=set)
    
    def get_transition_table(self) -> Dict:
        """
        获取转换表的字典表示，便于序列化和外部使用
        
        返回: {state: {symbol: next_state}}
        """
        table = {}
        for (state, symbol), next_state in self.transitions.items():
            if state not in table:
                table[state] = {}
            table[state][symbol] = next_state
        return table
