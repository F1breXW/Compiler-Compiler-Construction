"""
LALR(1)压缩算法
"""

from typing import List, FrozenSet, Dict, Tuple
from collections import defaultdict
from .lr_item import LR1Item


class LALRBuilder:
    """LALR(1)构建器 - 通过合并LR(1)同心项实现"""
    
    @staticmethod
    def merge(lr1_states: List[FrozenSet[LR1Item]], 
              lr1_goto: Dict[Tuple[int, str], int]) -> Tuple[List[FrozenSet[LR1Item]], Dict]:
        """
        将LR(1)项目集合并为LALR(1)状态
        
        算法原理:
        1. 识别"同心项"(core-identical items): 两个LR(1)状态如果除了向前看符号外完全相同，
           则它们具有相同的核心
        2. 将具有相同核心的状态合并: 合并它们的向前看符号
        3. 更新转移关系
        
        参数:
            lr1_states: LR(1)状态列表
            lr1_goto: LR(1)转移表
        返回: (lalr_states, lalr_goto)
        """
        print("  [合并LR(1)为LALR(1)]")
        
        # 按核心分组LR(1)状态
        core_groups: Dict[FrozenSet[Tuple[int, int]], List[int]] = defaultdict(list)
        
        for state_id, state in enumerate(lr1_states):
            # 提取核心(不含向前看符号)
            core = frozenset(item.core() for item in state)
            core_groups[core].append(state_id)
        
        # 构建LALR(1)状态
        lalr_states = []
        lr1_to_lalr: Dict[int, int] = {}
        
        for core, lr1_ids in core_groups.items():
            # 合并所有同心状态
            # 收集所有项目，合并向前看符号
            item_map: Dict[Tuple[int, int], set] = defaultdict(set)
            
            for lr1_id in lr1_ids:
                for item in lr1_states[lr1_id]:
                    item_map[item.core()].add(item.lookahead)
            
            # 重建项目集
            merged_items = set()
            for (prod_id, dot_pos), lookaheads in item_map.items():
                # 从第一个LR(1)状态获取产生式
                for lr1_id in lr1_ids:
                    for item in lr1_states[lr1_id]:
                        if item.core() == (prod_id, dot_pos):
                            production = item.production
                            break
                    else:
                        continue
                    break
                
                for lookahead in lookaheads:
                    merged_items.add(LR1Item(production, dot_pos, lookahead))
            
            # 创建LALR状态
            lalr_id = len(lalr_states)
            lalr_states.append(frozenset(merged_items))
            
            for lr1_id in lr1_ids:
                lr1_to_lalr[lr1_id] = lalr_id
        
        # 更新转移关系
        lalr_goto = {}
        for (lr1_state, symbol), lr1_next in lr1_goto.items():
            lalr_state = lr1_to_lalr[lr1_state]
            lalr_next = lr1_to_lalr[lr1_next]
            lalr_goto[(lalr_state, symbol)] = lalr_next
        
        print(f"    完成! LALR(1)状态数: {len(lalr_states)} (从{len(lr1_states)}个LR(1)状态压缩)")
        
        return lalr_states, lalr_goto
