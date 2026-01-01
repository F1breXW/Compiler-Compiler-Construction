"""
语法树可视化工具
"""

import json
from typing import Optional
from .parse_tree import ParseTreeNode


class ParseTreeVisualizer:
    """
    语法树可视化器
    支持多种输出格式：文本、JSON、DOT（Graphviz）
    """
    
    @staticmethod
    def to_text(root: ParseTreeNode) -> str:
        """
        转换为文本格式（树形结构）
        """
        if not root:
            return "空树"
        return str(root)
    
    @staticmethod
    def to_json(root: ParseTreeNode, filename: str = None) -> str:
        """
        转换为JSON格式
        
        参数:
            root: 根节点
            filename: 如果提供，则保存到文件
        返回:
            JSON字符串
        """
        if not root:
            tree_dict = {"error": "空树"}
        else:
            tree_dict = root.to_dict()
        
        json_str = json.dumps(tree_dict, ensure_ascii=False, indent=2)
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str
    
    @staticmethod
    def to_dot(root: ParseTreeNode, filename: str) -> bool:
        """
        转换为DOT格式（Graphviz可视化）
        
        参数:
            root: 根节点
            filename: 输出文件名
        返回:
            True if success
        """
        if not root:
            return False
        
        dot_lines = ['digraph ParseTree {']
        dot_lines.append('    node [shape=box, fontname="Helvetica"];')
        dot_lines.append('    edge [fontname="Helvetica"];')
        
        node_counter = [0]  # 使用列表以便在闭包中修改
        
        def add_node(node: ParseTreeNode, parent_id: Optional[int] = None) -> int:
            """递归添加节点"""
            current_id = node_counter[0]
            node_counter[0] += 1
            
            # 节点标签
            label = node.symbol
            if node.value is not None:
                label += f"\\n{node.value}"
            if node.production:
                label += f"\\n[{node.production}]"
            
            # 节点颜色：终结符用绿色，非终结符用蓝色
            color = "lightgreen" if node.is_terminal() else "lightblue"
            
            dot_lines.append(f'    node{current_id} [label="{label}", fillcolor="{color}", style=filled];')
            
            # 添加边
            if parent_id is not None:
                dot_lines.append(f'    node{parent_id} -> node{current_id};')
            
            # 递归处理子节点
            for child in node.children:
                add_node(child, current_id)
            
            return current_id
        
        add_node(root)
        dot_lines.append('}')
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(dot_lines))
            return True
        except Exception as e:
            print(f"保存DOT文件失败: {e}")
            return False
    
    @staticmethod
    def print_compact(root: ParseTreeNode, max_depth: int = 5):
        """
        紧凑格式打印（限制深度）
        
        参数:
            root: 根节点
            max_depth: 最大显示深度
        """
        if not root:
            print("空树")
            return
        
        def print_node(node: ParseTreeNode, depth: int, prefix: str = ""):
            if depth > max_depth:
                print(f"{prefix}...")
                return
            
            # 打印当前节点
            label = node.symbol
            if node.value is not None:
                label += f"({node.value})"
            
            print(f"{prefix}{label}")
            
            # 打印子节点
            for i, child in enumerate(node.children):
                is_last = (i == len(node.children) - 1)
                child_prefix = prefix + ("└── " if is_last else "├── ")
                next_prefix = prefix + ("    " if is_last else "│   ")
                
                if child.is_terminal():
                    term_label = child.symbol
                    if child.value is not None:
                        term_label += f"({child.value})"
                    print(f"{child_prefix}{term_label}")
                else:
                    print(f"{child_prefix}{child.symbol}")
                    for j, grandchild in enumerate(child.children):
                        is_last_grand = (j == len(child.children) - 1)
                        grandchild_prefix = next_prefix + ("└── " if is_last_grand else "├── ")
                        print_node(grandchild, depth + 1, grandchild_prefix)
        
        print_node(root, 0)
