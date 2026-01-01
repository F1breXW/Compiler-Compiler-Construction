"""
语法树节点定义
使用组合模式 (Composite Pattern) 构建语法树
"""

from typing import List, Optional, Any
from dataclasses import dataclass


@dataclass
class ParseTreeNode:
    """
    语法树节点（组合模式）
    既可以表示终结符（叶子节点），也可以表示非终结符（内部节点）
    """
    symbol: str  # 符号名称
    value: Any = None  # 符号值（对于终结符）
    children: List['ParseTreeNode'] = None  # 子节点列表
    production: str = None  # 使用的产生式（对于非终结符）
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    def is_terminal(self) -> bool:
        """判断是否为终结符（叶子节点）"""
        return len(self.children) == 0
    
    def add_child(self, child: 'ParseTreeNode'):
        """添加子节点"""
        self.children.append(child)
    
    def to_dict(self) -> dict:
        """转换为字典格式（便于JSON序列化）"""
        result = {
            'symbol': self.symbol,
            'value': str(self.value) if self.value is not None else None,
            'is_terminal': self.is_terminal()
        }
        
        if self.production:
            result['production'] = self.production
            
        if self.children:
            result['children'] = [child.to_dict() for child in self.children]
            
        return result
    
    def __str__(self, level=0) -> str:
        """树形打印"""
        indent = "  " * level
        result = f"{indent}{self.symbol}"
        
        if self.value is not None:
            result += f" ({self.value})"
        
        if self.production:
            result += f" [{self.production}]"
            
        result += "\n"
        
        for child in self.children:
            result += child.__str__(level + 1)
            
        return result


class ParseTreeBuilder:
    """
    语法树构建器（Builder模式）
    负责在LR分析过程中构建语法树
    """
    
    def __init__(self):
        self.node_stack: List[ParseTreeNode] = []
    
    def push_terminal(self, symbol: str, value: Any):
        """压入终结符节点（shift操作）"""
        node = ParseTreeNode(symbol=symbol, value=value)
        self.node_stack.append(node)
    
    def reduce(self, production_str: str, left: str, right: List[str]) -> ParseTreeNode:
        """
        归约操作（reduce）
        从栈中弹出右部符号对应的节点，构建新的父节点
        
        参数:
            production_str: 产生式字符串表示
            left: 产生式左部
            right: 产生式右部符号列表
        返回:
            新构建的父节点
        """
        # 处理空产生式
        if right == ['ε'] or not right:
            node = ParseTreeNode(symbol=left, production=production_str)
            self.node_stack.append(node)
            return node
        
        # 弹出右部对应的节点
        children = []
        for _ in range(len(right)):
            if self.node_stack:
                children.insert(0, self.node_stack.pop())
        
        # 创建父节点
        parent = ParseTreeNode(
            symbol=left,
            production=production_str,
            children=children
        )
        
        self.node_stack.append(parent)
        return parent
    
    def get_root(self) -> Optional[ParseTreeNode]:
        """获取根节点"""
        if self.node_stack:
            return self.node_stack[-1]
        return None
    
    def clear(self):
        """清空栈"""
        self.node_stack.clear()
