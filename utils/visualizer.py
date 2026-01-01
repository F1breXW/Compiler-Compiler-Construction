"""
可视化工具类
负责将自动机转换为Graphviz DOT格式
"""

from lexical.nfa import NFA
from lexical.dfa import DFA

class GraphvizVisualizer:
    """
    Graphviz可视化生成器
    遵循单一职责原则，专门负责图形化输出
    """
    
    @staticmethod
    def _format_edge_label(chars: list) -> str:
        """
        格式化边标签，合并连续字符
        例如: ['a', 'b', 'c'] -> "a-c"
        """
        if not chars:
            return ""
            
        # 过滤None (epsilon)
        valid_chars = [c for c in chars if c is not None]
        has_epsilon = None in chars
        
        if not valid_chars:
            return "ε" if has_epsilon else ""
            
        valid_chars.sort()
        
        # 尝试识别常见集合
        chars_set = set(valid_chars)
        if set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") <= chars_set:
             # 如果包含所有字母，简化显示
             return "letter" + (", ε" if has_epsilon else "")
        if set("0123456789") <= chars_set:
             return "digit" + (", ε" if has_epsilon else "")
             
        # 范围合并算法
        ranges = []
        if valid_chars:
            start = valid_chars[0]
            end = valid_chars[0]
            
            for i in range(1, len(valid_chars)):
                char = valid_chars[i]
                # 检查是否连续 (基于ASCII码)
                if ord(char) == ord(end) + 1:
                    end = char
                else:
                    # 结束当前范围
                    if start == end:
                        ranges.append(start)
                    elif ord(end) - ord(start) == 1:
                        ranges.append(f"{start},{end}")
                    else:
                        ranges.append(f"{start}-{end}")
                    start = char
                    end = char
            
            # 添加最后一个范围
            if start == end:
                ranges.append(start)
            elif ord(end) - ord(start) == 1:
                ranges.append(f"{start},{end}")
            else:
                ranges.append(f"{start}-{end}")
                
        label = ",".join(ranges)
        if has_epsilon:
            label = f"ε,{label}" if label else "ε"
            
        return label.replace('"', '\\"')

    @staticmethod
    def export_nfa(nfa: NFA, filename: str, title: str = "NFA"):
        """
        导出NFA为DOT文件
        """
        dot_content = ['digraph NFA {']
        dot_content.append(f'    labelloc="t";')
        dot_content.append(f'    label="{title}";')
        dot_content.append('    rankdir=LR;')
        dot_content.append('    node [shape=circle, fontname="Helvetica"];')
        dot_content.append('    edge [fontname="Helvetica"];')
        
        # 标记起始状态
        if nfa.start_state:
            dot_content.append('    start [shape=point];')
            dot_content.append(f'    start -> "{nfa.start_state.id}";')
            
        # 标记接受状态
        for state in nfa.accept_states:
            dot_content.append(f'    "{state.id}" [shape=doublecircle];')
            if state.tag:
                dot_content.append(f'    "{state.id}" [xlabel="{state.tag}"];')

        # 合并转换边
        # transitions: {(from_state, symbol): {to_states}}
        # 需要转换为: {(from_state, to_state): [symbols]}
        grouped_transitions = {}
        
        for (from_state, symbol), to_states in nfa.transitions.items():
            for to_state in to_states:
                key = (from_state.id, to_state.id)
                if key not in grouped_transitions:
                    grouped_transitions[key] = []
                grouped_transitions[key].append(symbol)
                
        for (from_id, to_id), symbols in grouped_transitions.items():
            label = GraphvizVisualizer._format_edge_label(symbols)
            dot_content.append(f'    "{from_id}" -> "{to_id}" [label="{label}"];')
                
        dot_content.append('}')
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(dot_content))
            return True
        except Exception as e:
            print(f"导出DOT文件失败: {e}")
            return False
            
    @staticmethod
    def export_dfa(dfa: DFA, filename: str, title: str = "DFA"):
        """
        导出DFA为DOT文件
        """
        dot_content = ['digraph DFA {']
        dot_content.append(f'    labelloc="t";')
        dot_content.append(f'    label="{title}";')
        dot_content.append('    rankdir=LR;')
        dot_content.append('    node [shape=circle, fontname="Helvetica"];')
        dot_content.append('    edge [fontname="Helvetica"];')
        
        # 标记起始状态
        dot_content.append('    start [shape=point];')
        dot_content.append(f'    start -> "{dfa.start_state}";')
            
        # 标记接受状态
        for state in dfa.accept_states:
            dot_content.append(f'    "{state}" [shape=doublecircle];')
            tag = dfa.accept_tags.get(state)
            if tag:
                dot_content.append(f'    "{state}" [xlabel="{tag}"];')

        # 合并转换边
        # transitions: {(from_state, symbol): to_state}
        # 需要转换为: {(from_state, to_state): [symbols]}
        grouped_transitions = {}
        
        for (from_state, symbol), to_state in dfa.transitions.items():
            key = (from_state, to_state)
            if key not in grouped_transitions:
                grouped_transitions[key] = []
            grouped_transitions[key].append(symbol)
            
        for (from_id, to_id), symbols in grouped_transitions.items():
            label = GraphvizVisualizer._format_edge_label(symbols)
            dot_content.append(f'    "{from_id}" -> "{to_id}" [label="{label}"];')
                
        dot_content.append('}')
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(dot_content))
            return True
        except Exception as e:
            print(f"导出DOT文件失败: {e}")
            return False
