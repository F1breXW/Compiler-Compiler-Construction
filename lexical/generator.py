"""
词法分析生成器主类
"""

from typing import Tuple, Dict, Set
from .state import State
from .thompson import ThompsonConstructor
from .subset_construction import SubsetConstructor
from .minimization import DFAMinimizer


class LexicalGenerator:
    """
    词法分析生成器
    负责将正则表达式转换为最小化的DFA，并生成词法分析表
    """
    
    def __init__(self):
        """初始化词法生成器，设置状态计数器"""
        self.state_counter = 0
        self.thompson = ThompsonConstructor(self._new_state)
        self.subset_constructor = SubsetConstructor()
        self.minimizer = DFAMinimizer()
    
    def _new_state(self, is_accepting: bool = False, tag: str = None) -> State:
        """
        创建新状态
        
        参数:
            is_accepting: 是否为接受状态
            tag: 状态标签
        返回: 新创建的状态对象
        """
        state = State(self.state_counter, is_accepting, tag)
        self.state_counter += 1
        return state
    
    def generate(self, regex: str, token_tag: str = "TOKEN") -> Tuple[Dict, Set[int]]:
        """
        主接口: 从正则表达式生成词法分析表
        
        流程: RE -> NFA -> DFA -> 最小化DFA -> 输出转换表
        
        参数:
            regex: 正则表达式
            token_tag: token类型标签
        返回: (transition_table, accepting_states)
            - transition_table: {state: {symbol: next_state}}
            - accepting_states: 接受状态集合
        """
        print(f"[词法生成器] 开始处理正则表达式: {regex}")
        
        # 步骤1: RE -> NFA (Thompson构造)
        print("  [1/4] Thompson构造法: RE -> NFA")
        nfa = self.thompson.construct_simple(regex, token_tag)
        print(f"    NFA状态数: {len(nfa.states)}")
        
        # 步骤2: NFA -> DFA (子集构造)
        print("  [2/4] 子集构造法: NFA -> DFA")
        dfa = self.subset_constructor.construct(nfa)
        print(f"    DFA状态数: {len(dfa.states)}")
        
        # 步骤3: DFA最小化
        print("  [3/4] 等价状态分割: DFA最小化")
        min_dfa = self.minimizer.minimize(dfa)
        print(f"    最小化DFA状态数: {len(min_dfa.states)}")
        
        # 步骤4: 输出转换表
        print("  [4/4] 生成转换表")
        transition_table = min_dfa.get_transition_table()
        accepting_states = min_dfa.accept_states
        
        print(f"[词法生成器] 完成! 接受状态: {accepting_states}\n")
        
        return transition_table, accepting_states
