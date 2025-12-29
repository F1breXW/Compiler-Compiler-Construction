"""
语义分析器基类
"""

from typing import List, Dict, Any, Optional
from syntax.grammar import Production
from .symbol import Symbol


class SemanticAnalyzer:
    """
    语义分析器基类 - 供同学B继承和扩展
    
    提供了一些常用的语义分析功能:
    - 符号表管理
    - 临时变量生成
    - 中间代码生成
    """
    
    def __init__(self):
        """初始化语义分析器"""
        # 符号表: {变量名: 类型/值}
        self.symbol_table: Dict[str, Any] = {}
        
        # 临时变量计数器
        self.temp_counter = 0
        
        # 三地址码序列
        self.intermediate_code: List[str] = []
    
    def new_temp(self) -> str:
        """
        生成新的临时变量
        
        返回: 临时变量名，如t1, t2, ...
        """
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def emit(self, code: str):
        """
        生成一条三地址码
        
        参数:
            code: 三地址码语句
        """
        self.intermediate_code.append(code)
        print(f"      [生成代码] {code}")
    
    def add_symbol(self, name: str, type_or_value: Any):
        """
        向符号表添加符号
        
        参数:
            name: 符号名
            type_or_value: 类型或值
        """
        self.symbol_table[name] = type_or_value
        print(f"      [符号表] 添加: {name} = {type_or_value}")
    
    def lookup_symbol(self, name: str) -> Optional[Any]:
        """
        查找符号表
        
        参数:
            name: 符号名
        返回: 符号的类型/值，或None
        """
        return self.symbol_table.get(name)
    
    def semantic_action(self, production: Production, symbols: List[Symbol]) -> Any:
        """
        语义动作处理函数 - 子类应重写此方法
        
        这是一个模板方法，同学B应该根据具体的语法制导翻译方案重写
        
        参数:
            production: 产生式
            symbols: 归约的符号列表
        返回: 综合属性值
        """
        # 默认实现: 什么都不做
        return None
    
    def get_code(self) -> List[str]:
        """获取生成的中间代码"""
        return self.intermediate_code
    
    def print_symbol_table(self):
        """打印符号表"""
        print("\n=== 符号表 ===")
        for name, value in self.symbol_table.items():
            print(f"  {name}: {value}")
    
    def print_intermediate_code(self):
        """打印中间代码"""
        print("\n=== 三地址码 ===")
        for i, code in enumerate(self.intermediate_code, 1):
            print(f"  {i}: {code}")
