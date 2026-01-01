"""
词法分析生成器主类
"""

from typing import Tuple, Dict, Set
from .state import State
from .thompson import ThompsonConstructor
from .subset_construction import SubsetConstructor
from .minimization import DFAMinimizer
from .regex_parser import RegexParser


class   LexicalGenerator:
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
        self.regex_parser = RegexParser(self.thompson)
        
        # 存储中间产物，用于可视化或调试
        self.last_nfa = None
        self.last_dfa = None
        self.last_min_dfa = None
    
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
        
        # 构建接受状态ID到Tag的映射
        accepting_map = {}
        for state in min_dfa.accept_states:
            if state.tag:
                accepting_map[state.id] = state.tag
            else:
                accepting_map[state.id] = token_tag
        
        print(f"[词法生成器] 完成! 接受状态: {list(accepting_map.keys())}\n")
        
        return transition_table, accepting_map

    def build(self, rules: list) -> Tuple[Dict, Dict[int, str]]:
        """
        构建包含多条规则的词法分析器
        
        参数:
            rules: 规则列表 [(regex, tag), ...]
                   支持特殊regex: "id" (标识符), "num" (数字)
        返回:
            (transition_table, accepting_map)
            accepting_map: {state_id: token_tag}
        """
        print(f"[词法生成器] 开始构建多规则词法分析器 (规则数: {len(rules)})")
        
        # 1. 为每条规则构建NFA
        nfas = []
        for i, (regex, tag) in enumerate(rules):
            if regex == "id":
                nfa = self.thompson.construct_identifier(tag)
            elif regex == "num":
                nfa = self.thompson.construct_number(tag)
            else:
                # 尝试解析正则表达式
                try:
                    nfa = self.regex_parser.parse(regex, tag)
                except Exception as e:
                    print(f"  [警告] 正则解析失败 '{regex}': {e}，回退到简单字符串构造")
                    nfa = self.thompson.construct_simple(regex, tag)
            
            # 设置优先级 (规则索引越小优先级越高)
            for state in nfa.accept_states:
                state.priority = i
                
            nfas.append(nfa)
                
        # 2. 合并所有NFA
        # 创建一个新的起始状态，通过epsilon连接到所有NFA的起始状态
        from .nfa import NFA
        combined_nfa = NFA()
        start_state = self._new_state()
        combined_nfa.start_state = start_state
        combined_nfa.states.add(start_state)
        
        for nfa in nfas:
            combined_nfa.states.update(nfa.states)
            combined_nfa.alphabet.update(nfa.alphabet)
            combined_nfa.transitions.update(nfa.transitions)
            combined_nfa.accept_states.update(nfa.accept_states)
            
            # 添加epsilon转换: start -> nfa.start
            combined_nfa.add_transition(start_state, None, nfa.start_state)
            
        print(f"  [1/3] NFA合并完成 (总状态数: {len(combined_nfa.states)})")
        self.last_nfa = combined_nfa
        
        # 3. NFA -> DFA
        print("  [2/3] 子集构造法: NFA -> DFA")
        dfa = self.subset_constructor.construct(combined_nfa)
        print(f"    DFA状态数: {len(dfa.states)}")
        self.last_dfa = dfa
        
        # 4. DFA最小化
        print("  [3/3] DFA最小化")
        min_dfa = self.minimizer.minimize(dfa)
        print(f"    最小化DFA状态数: {len(min_dfa.states)}")
        self.last_min_dfa = min_dfa
        
        # 5. 构建结果
        transition_table = min_dfa.get_transition_table()
        accepting_map = {}
        for state_id in min_dfa.accept_states:
            if state_id in min_dfa.accept_tags:
                accepting_map[state_id] = min_dfa.accept_tags[state_id]
                
        return transition_table, accepting_map
        start_state = self._new_state()
        combined_nfa.start_state = start_state
        combined_nfa.states.add(start_state)
        
        for nfa in nfas:
            combined_nfa.states.update(nfa.states)
            combined_nfa.alphabet.update(nfa.alphabet)
            combined_nfa.transitions.update(nfa.transitions)
            combined_nfa.accept_states.update(nfa.accept_states)
            
            # 添加epsilon转换: start -> nfa.start
            combined_nfa.add_transition(start_state, None, nfa.start_state)
            
        print(f"  [1/3] NFA合并完成 (总状态数: {len(combined_nfa.states)})")
        
        # 3. NFA -> DFA
        print("  [2/3] 子集构造法: NFA -> DFA")
        dfa = self.subset_constructor.construct(combined_nfa)
        print(f"    DFA状态数: {len(dfa.states)}")
        
        # 4. DFA最小化
        print("  [3/3] DFA最小化")
        min_dfa = self.minimizer.minimize(dfa)
        print(f"    最小化DFA状态数: {len(min_dfa.states)}")
        
        return min_dfa.get_transition_table(), min_dfa.accept_states
