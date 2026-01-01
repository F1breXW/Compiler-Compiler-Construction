"""
子集构造法: NFA转DFA
"""

from typing import Set, Dict, FrozenSet, Optional
from collections import deque
from .state import State
from .nfa import NFA
from .dfa import DFA


class SubsetConstructor:
    """子集构造算法实现"""
    
    @staticmethod
    def epsilon_closure(nfa: NFA, states: Set[State]) -> Set[State]:
        """
        计算epsilon闭包: 从给定状态集合出发，通过epsilon转换能到达的所有状态
        
        算法: 使用DFS/BFS遍历所有epsilon可达的状态
        
        参数:
            nfa: NFA对象
            states: 初始状态集合
        返回: epsilon闭包状态集合
        """
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            # 查找所有epsilon转换
            epsilon_transitions = nfa.transitions.get((state, None), set())
            for next_state in epsilon_transitions:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        
        return closure
    
    @staticmethod
    def move(nfa: NFA, states: Set[State], symbol: str) -> Set[State]:
        """
        Move操作: 从状态集合出发，通过输入符号symbol能到达的状态集合
        
        参数:
            nfa: NFA对象
            states: 源状态集合
            symbol: 输入符号
        返回: move后的状态集合
        """
        result = set()
        for state in states:
            next_states = nfa.transitions.get((state, symbol), set())
            result.update(next_states)
        return result
    
    @staticmethod
    def _get_accept_tag(states: FrozenSet[State]) -> Optional[str]:
        """获取状态集中优先级最高的接受标签"""
        best_tag = None
        best_priority = float('inf')
        
        for state in states:
            if state.is_accepting:
                if state.priority < best_priority:
                    best_priority = state.priority
                    best_tag = state.tag
        return best_tag

    def construct(self, nfa: NFA) -> DFA:
        """
        子集构造法: 将NFA转换为DFA
        
        算法原理:
        1. DFA的每个状态对应NFA状态的一个子集
        2. 初始状态 = epsilon_closure(nfa.start_state)
        3. 对于每个未处理的DFA状态和每个输入符号:
           - 计算 move(当前状态集, 符号)
           - 计算 epsilon_closure(move结果)
           - 如果得到新状态集，加入DFA
        4. 如果DFA状态包含NFA的接受状态，则该DFA状态也是接受状态
        
        参数:
            nfa: 输入的NFA
        返回: 转换得到的DFA
        """
        dfa = DFA()
        dfa.alphabet = nfa.alphabet.copy()
        
        # 计算初始状态的epsilon闭包
        start_closure = frozenset(self.epsilon_closure(nfa, {nfa.start_state}))
        
        # DFA状态映射: frozenset(NFA状态集) -> DFA状态ID
        state_map: Dict[FrozenSet[State], int] = {}
        state_map[start_closure] = 0
        dfa.start_state = 0
        dfa.states.add(0)
        
        # 检查初始状态是否为接受状态
        tag = self._get_accept_tag(start_closure)
        if tag is not None:
            dfa.accept_states.add(0)
            dfa.accept_tags[0] = tag
        
        # 工作队列: 未处理的DFA状态
        worklist = deque([start_closure])
        
        while worklist:
            current_nfa_states = worklist.popleft()
            current_dfa_state = state_map[current_nfa_states]
            
            # 对每个输入符号
            for symbol in dfa.alphabet:
                # 计算 move 和 epsilon闭包
                next_nfa_states = self.move(nfa, current_nfa_states, symbol)
                next_closure = frozenset(self.epsilon_closure(nfa, next_nfa_states))
                
                if not next_closure:
                    continue
                
                # 如果是新状态，加入DFA
                if next_closure not in state_map:
                    new_dfa_state = len(state_map)
                    state_map[next_closure] = new_dfa_state
                    dfa.states.add(new_dfa_state)
                    worklist.append(next_closure)
                    
                    # 检查是否为接受状态
                    tag = self._get_accept_tag(next_closure)
                    if tag is not None:
                        dfa.accept_states.add(new_dfa_state)
                        dfa.accept_tags[new_dfa_state] = tag
                
                # 添加转换
                next_dfa_state = state_map[next_closure]
                dfa.transitions[(current_dfa_state, symbol)] = next_dfa_state
        
        return dfa
