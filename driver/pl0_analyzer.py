"""
PL/0语义分析器示例
"""

from typing import List, Any
from syntax.grammar import Production
from .semantic_analyzer import SemanticAnalyzer
from .symbol import Symbol


class PL0SemanticAnalyzer(SemanticAnalyzer):
    """
    PL/0语言的语义分析器示例
    同学B可以参考此类实现自己的语义分析器
    """
    
    def semantic_action(self, production: Production, symbols: List[Symbol]) -> Any:
        """
        PL/0的语义动作实现示例
        
        注意: 这只是一个简化的示例，实际的PL/0语义分析会更复杂
        """
        prod_str = str(production)

        if len(symbols) == 3:
            if symbols[1].value in ['+','-','*','/']:
                # 二元运算: E -> E op T
                left = symbols[0].value
                op = symbols[1].name
                right = symbols[2].value
                
                temp = self.new_temp()
                self.emit(f"{temp} = {left} {op} {right}")
                return temp
            elif "(" in prod_str:
                return symbols[1].value
        
        # 示例: 赋值语句
        if ":=" in prod_str:
            if len(symbols) == 3:
                # id := expression
                var_name = symbols[0].value
                expr_value = symbols[2].value
                self.emit(f"{var_name} = {expr_value}")
                return None
        
        # 默认: 传递第一个符号的值
        if symbols:
            return symbols[0].value
        return None
