"""
文件I/O工具函数
"""

import json
from typing import Any, Dict


def save_json(data: Any, filename: str):
    """
    将数据保存为JSON文件
    
    参数:
        data: 要保存的数据
        filename: 文件名
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filename: str) -> Any:
    """
    从JSON文件加载数据
    
    参数:
        filename: 文件名
    返回: 加载的数据
    """
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_parsing_tables(action_table: Dict, goto_table: Dict, filename: str = "parsing_tables.json"):
    """
    保存分析表到JSON文件
    
    参数:
        action_table: ACTION表
        goto_table: GOTO表
        filename: 文件名
    """
    # 转换为可序列化的格式
    action_dict = {}
    for (state, symbol), (action, value) in action_table.items():
        key = f"({state}, {symbol})"
        action_dict[key] = {"action": action, "value": value}
    
    goto_dict = {}
    for (state, symbol), next_state in goto_table.items():
        key = f"({state}, {symbol})"
        goto_dict[key] = next_state
    
    tables = {
        "action_table": action_dict,
        "goto_table": goto_dict,
        "info": {
            "action_entries": len(action_table),
            "goto_entries": len(goto_table)
        }
    }
    
    save_json(tables, filename)
    print(f"\n✓ 分析表已保存到 {filename}")
