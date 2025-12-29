"""
Thompson构造法: 正则表达式转NFA
"""

from typing import Callable
from .state import State
from .nfa import NFA


class ThompsonConstructor:
    """Thompson构造算法实现"""
    
    def __init__(self, state_factory: Callable[[], State]):
        """
        初始化Thompson构造器
        
        参数:
            state_factory: 状态工厂函数，用于生成新状态
        """
        self.new_state = state_factory
    
    def construct_char(self, char: str) -> NFA:
        """
        构造单个字符的NFA
        创建: start -char-> accept
        
        参数:
            char: 输入字符
        返回: NFA
        """
        nfa = NFA()
        start = self.new_state()
        accept = self.new_state()
        accept.is_accepting = True
        
        nfa.start_state = start
        nfa.accept_states.add(accept)
        nfa.add_transition(start, char, accept)
        
        return nfa
    
    def construct_concat(self, nfa1: NFA, nfa2: NFA) -> NFA:
        """
        构造连接操作的NFA (AB)
        将nfa1的接受状态通过epsilon连接到nfa2的起始状态
        
        参数:
            nfa1: 第一个NFA
            nfa2: 第二个NFA
        返回: 连接后的NFA
        """
        nfa = NFA()
        nfa.states = nfa1.states | nfa2.states
        nfa.alphabet = nfa1.alphabet | nfa2.alphabet
        nfa.transitions = {**nfa1.transitions, **nfa2.transitions}
        nfa.start_state = nfa1.start_state
        nfa.accept_states = nfa2.accept_states
        
        # 将nfa1的所有接受状态连接到nfa2的起始状态
        for accept in nfa1.accept_states:
            accept.is_accepting = False
            nfa.add_transition(accept, None, nfa2.start_state)
        
        return nfa
    
    def construct_union(self, nfa1: NFA, nfa2: NFA) -> NFA:
        """
        构造选择操作的NFA (A|B)
        创建新的起始和接受状态，用epsilon连接两个NFA
        
        参数:
            nfa1: 第一个NFA
            nfa2: 第二个NFA
        返回: 选择后的NFA
        """
        nfa = NFA()
        new_start = self.new_state()
        new_accept = self.new_state()
        new_accept.is_accepting = True
        
        nfa.states = nfa1.states | nfa2.states | {new_start, new_accept}
        nfa.alphabet = nfa1.alphabet | nfa2.alphabet
        nfa.transitions = {**nfa1.transitions, **nfa2.transitions}
        nfa.start_state = new_start
        nfa.accept_states = {new_accept}
        
        # 从新起始状态到两个NFA的起始状态
        nfa.add_transition(new_start, None, nfa1.start_state)
        nfa.add_transition(new_start, None, nfa2.start_state)
        
        # 从两个NFA的接受状态到新接受状态
        for accept in nfa1.accept_states:
            accept.is_accepting = False
            nfa.add_transition(accept, None, new_accept)
        for accept in nfa2.accept_states:
            accept.is_accepting = False
            nfa.add_transition(accept, None, new_accept)
        
        return nfa
    
    def construct_star(self, nfa1: NFA) -> NFA:
        """
        构造Kleene闭包的NFA (A*)
        创建新的起始和接受状态，添加epsilon回边和跳过边
        
        参数:
            nfa1: 输入NFA
        返回: 闭包后的NFA
        """
        nfa = NFA()
        new_start = self.new_state()
        new_accept = self.new_state()
        new_accept.is_accepting = True
        
        nfa.states = nfa1.states | {new_start, new_accept}
        nfa.alphabet = nfa1.alphabet
        nfa.transitions = nfa1.transitions.copy()
        nfa.start_state = new_start
        nfa.accept_states = {new_accept}
        
        # epsilon边: new_start -> nfa1.start
        nfa.add_transition(new_start, None, nfa1.start_state)
        
        # epsilon边: nfa1的接受状态 -> new_accept
        for accept in nfa1.accept_states:
            accept.is_accepting = False
            nfa.add_transition(accept, None, new_accept)
            # epsilon回边: accept -> nfa1.start (实现闭包)
            nfa.add_transition(accept, None, nfa1.start_state)
        
        # epsilon跳过边: new_start -> new_accept (允许匹配0次)
        nfa.add_transition(new_start, None, new_accept)
        
        return nfa
    
    def construct_simple(self, regex: str, token_tag: str) -> NFA:
        """
        构造简单正则表达式的NFA (字符序列)
        
        注意: 这是简化实现，完整实现需要递归下降解析器
        
        参数:
            regex: 正则表达式字符串
            token_tag: token类型标签
        返回: NFA
        """
        nfa = NFA()
        start = self.new_state()
        nfa.start_state = start
        current = start
        
        # 创建状态链
        for char in regex:
            next_state = self.new_state()
            nfa.add_transition(current, char, next_state)
            current = next_state
        
        # 最后一个状态设为接受状态
        current.is_accepting = True
        current.tag = token_tag
        nfa.accept_states.add(current)
        
        return nfa
