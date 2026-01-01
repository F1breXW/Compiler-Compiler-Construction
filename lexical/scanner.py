"""
词法扫描器 (Scanner)
负责使用DFA转换表将源代码字符串转换为Token列表
"""

from typing import List, Tuple, Dict, Optional


class Scanner:
    """
    词法扫描器
    """
    
    def __init__(self, transition_table: Dict[int, Dict[str, int]], accepting_map: Dict[int, str]):
        """
        初始化扫描器
        
        参数:
            transition_table: DFA转换表 {state: {char: next_state}}
            accepting_map: 接受状态映射 {state_id: token_tag}
        """
        self.transition_table = transition_table
        self.accepting_map = accepting_map
        
    def scan(self, source_code: str) -> List[Tuple[str, str]]:
        """
        扫描源代码并生成Token列表 (最大匹配原则)
        
        参数:
            source_code: 源代码字符串
            
        返回:
            Token列表 [(type, value), ...]
        """
        tokens = []
        pos = 0
        length = len(source_code)
        
        while pos < length:
            # 1. 跳过空白字符
            if source_code[pos].isspace():
                pos += 1
                continue
                
            # 2. 尝试寻找最长匹配
            longest_match_text = None
            longest_match_tag = None
            longest_match_end = -1
            
            current_state = 0  # 假设初始状态总是0
            current_pos = pos
            
            while current_pos < length:
                char = source_code[current_pos]
                
                # 检查是否有转换
                if current_state in self.transition_table and char in self.transition_table[current_state]:
                    current_state = self.transition_table[current_state][char]
                    current_pos += 1
                    
                    # 如果是接受状态，记录匹配
                    if current_state in self.accepting_map:
                        longest_match_text = source_code[pos:current_pos]
                        longest_match_tag = self.accepting_map[current_state]
                        longest_match_end = current_pos
                else:
                    break
            
            # 3. 处理匹配结果
            if longest_match_text:
                tokens.append((longest_match_tag, longest_match_text))
                pos = longest_match_end
            else:
                # 匹配失败，跳过一个字符并报错(或作为未知字符)
                # print(f"[Scanner] 警告: 无法识别的字符 '{source_code[pos]}' at position {pos}")
                pos += 1
                
        return tokens
