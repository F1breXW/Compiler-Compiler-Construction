"""
DFA最小化算法
"""

from typing import List, Set
from collections import defaultdict
from .dfa import DFA


class DFAMinimizer:
    """DFA最小化算法实现 (Hopcroft算法)"""
    
    @staticmethod
    def minimize(dfa: DFA) -> DFA:
        """
        DFA最小化: 使用等价状态分割法
        
        算法原理:
        1. 初始划分: 将状态分为"接受状态"和"非接受状态"两组
        2. 迭代细化: 对于每个分组，检查其中的状态在相同输入下是否转移到同一分组
           - 如果不是，则将该组分裂
        3. 重复步骤2，直到不能再分裂为止
        4. 每个最终的分组对应最小化DFA的一个状态
        
        参数:
            dfa: 输入的DFA
        返回: 最小化后的DFA
        """
        # 初始划分: 接受状态 vs 非接受状态
        accept_group = dfa.accept_states
        non_accept_group = dfa.states - dfa.accept_states
        
        # 分组列表
        partitions = []
        if accept_group:
            partitions.append(accept_group)
        if non_accept_group:
            partitions.append(non_accept_group)
        
        def get_group_id(state: int, partitions: List[Set[int]]) -> int:
            """获取状态所属的分组ID"""
            for i, group in enumerate(partitions):
                if state in group:
                    return i
            return -1
        
        # 迭代细化分组
        changed = True
        while changed:
            changed = False
            new_partitions = []
            
            for group in partitions:
                if len(group) <= 1:
                    new_partitions.append(group)
                    continue
                
                # 尝试分裂当前分组
                # 按照"对于所有输入符号，转移到的分组序列"对状态分类
                signature_map = defaultdict(set)
                
                for state in group:
                    signature = []
                    for symbol in sorted(dfa.alphabet):
                        next_state = dfa.transitions.get((state, symbol), -1)
                        if next_state == -1:
                            signature.append(-1)
                        else:
                            signature.append(get_group_id(next_state, partitions))
                    signature_map[tuple(signature)].add(state)
                
                # 如果分裂出多个子组，则标记changed
                if len(signature_map) > 1:
                    changed = True
                    new_partitions.extend(signature_map.values())
                else:
                    new_partitions.append(group)
            
            partitions = new_partitions
        
        # 构建最小化的DFA
        min_dfa = DFA()
        min_dfa.alphabet = dfa.alphabet.copy()
        
        # 为每个分组分配新的状态ID
        group_to_id = {}
        for i, group in enumerate(partitions):
            group_to_id[frozenset(group)] = i
            min_dfa.states.add(i)
        
        # 确定起始状态和接受状态
        for group_fs, group_id in group_to_id.items():
            group = set(group_fs)
            if dfa.start_state in group:
                min_dfa.start_state = group_id
            if any(s in dfa.accept_states for s in group):
                min_dfa.accept_states.add(group_id)
        
        # 构建转换表
        for group_fs, group_id in group_to_id.items():
            group = set(group_fs)
            representative = next(iter(group))  # 任选一个代表状态
            
            for symbol in dfa.alphabet:
                next_state = dfa.transitions.get((representative, symbol))
                if next_state is not None:
                    # 找到next_state所在的分组
                    for target_group_fs, target_id in group_to_id.items():
                        if next_state in target_group_fs:
                            min_dfa.transitions[(group_id, symbol)] = target_id
                            break
        
        return min_dfa
