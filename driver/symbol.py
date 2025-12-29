"""
符号类定义
"""

from typing import Any, Dict
from dataclasses import dataclass, field


@dataclass
class Symbol:
    """
    符号类: 用于分析栈中的符号
    
    属性:
        name: 符号名称
        value: 符号的语义值(用于语义分析)
        attributes: 附加属性字典
    """
    name: str
    value: Any = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self):
        return f"Symbol({self.name}, {self.value})"
