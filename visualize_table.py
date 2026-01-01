#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LALR(1)分析表可视化工具
输出HTML格式的ACTION和GOTO表
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent))

from lexical import LexicalGenerator
from syntax import Grammar, ParserGenerator
from utils.config_loader import ConfigLoader


def generate_table_html(config_path: str, output_path: str = None, action_table=None, goto_table=None):
    """
    生成LALR(1)分析表的HTML可视化
    
    Args:
        config_path: 文法配置文件路径
        output_path: 输出HTML文件路径（默认: visualizations/{文法名}_table.html）
        action_table: 预生成的ACTION表（可选）
        goto_table: 预生成的GOTO表（可选）
    """
    # 加载配置
    loader = ConfigLoader(os.path.dirname(os.path.abspath(config_path)))
    config = loader.load(os.path.basename(config_path))
    
    # 总是构建文法对象，因为后续可视化需要用到产生式信息
    grammar = Grammar()
    for rule_str in config.grammar_rules:
        left, right = rule_str.split('->')
        left = left.strip()
        right = [s.strip() for s in right.strip().split()]
        grammar.add_production(left, right)
    
    if action_table is None or goto_table is None:
        # 生成语法分析器
        parser_generator = ParserGenerator(grammar)
        action_table, goto_table = parser_generator.generate()
    else:
        # 如果使用了预生成的表，必须手动增广文法以匹配产生式ID
        grammar.augment()
    
    # 获取所有状态和符号
    states = sorted(set(s for s, _ in action_table.keys()) | set(s for s, _ in goto_table.keys()))
    terminals = sorted(set(sym for _, sym in action_table.keys()))
    nonterminals = sorted(set(sym for _, sym in goto_table.keys()))
    
    # 设置默认输出路径
    if output_path is None:
        output_path = f"visualizations/{config.name.replace(' ', '_')}_lalr_table.html"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 生成HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>LALR(1)分析表 - {config.name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 100%;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
        }}
        .info {{
            background: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 4px solid #3498db;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-box {{
            flex: 1;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-box h3 {{
            margin: 0;
            font-size: 2em;
        }}
        .stat-box p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-size: 13px;
            background: white;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }}
        th {{
            background: #3498db;
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        th.state {{
            background: #2c3e50;
        }}
        th.terminal {{
            background: #27ae60;
        }}
        th.nonterminal {{
            background: #e67e22;
        }}
        tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        tr:hover {{
            background: #e3f2fd;
        }}
        .shift {{
            background: #c8e6c9;
            color: #2e7d32;
            font-weight: bold;
        }}
        .reduce {{
            background: #ffccbc;
            color: #d84315;
            font-weight: bold;
        }}
        .accept {{
            background: #b2dfdb;
            color: #00695c;
            font-weight: bold;
        }}
        .goto {{
            background: #fff9c4;
            color: #f57f17;
            font-weight: bold;
        }}
        .empty {{
            color: #bbb;
        }}
        .search-box {{
            margin: 20px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        .search-box input {{
            padding: 8px;
            width: 200px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .legend {{
            display: flex;
            gap: 15px;
            margin: 15px 0;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 LALR(1)分析表</h1>
        
        <div class="info">
            <strong>文法名称:</strong> {config.name}<br>
            <strong>描述:</strong> {config.description}
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <h3>{len(states)}</h3>
                <p>状态数量</p>
            </div>
            <div class="stat-box">
                <h3>{len(terminals)}</h3>
                <p>终结符</p>
            </div>
            <div class="stat-box">
                <h3>{len(nonterminals)}</h3>
                <p>非终结符</p>
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color shift"></div>
                <span>Shift (移进)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color reduce"></div>
                <span>Reduce (规约)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color accept"></div>
                <span>Accept (接受)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color goto"></div>
                <span>Goto (转移)</span>
            </div>
        </div>
        
        <div class="search-box">
            🔍 <input type="text" id="searchInput" placeholder="搜索状态或符号..." onkeyup="searchTable()">
            <button onclick="resetTable()">重置</button>
        </div>
        
        <h2>ACTION 表</h2>
        <table id="actionTable">
            <thead>
                <tr>
                    <th class="state">状态</th>
"""
    
    # ACTION表头
    for term in terminals:
        html += f'                    <th class="terminal">{term}</th>\n'
    html += """                </tr>
            </thead>
            <tbody>
"""
    
    # ACTION表内容
    for state in states:
        html += f'                <tr>\n'
        html += f'                    <th class="state">{state}</th>\n'
        for term in terminals:
            action = action_table.get((state, term))
            if action:
                action_type, action_val = action
                if action_type == 'accept':
                    cell_class = 'accept'
                    display = 'ACC'
                elif action_type == 'shift':
                    cell_class = 'shift'
                    display = f'S{action_val}'
                elif action_type == 'reduce':
                    cell_class = 'reduce'
                    prod = grammar.productions[action_val]
                    left = prod.left
                    right = ' '.join(prod.right) if prod.right else 'ε'
                    display = f'R{action_val}'
                    title = f'{left} → {right}'
                    html += f'                    <td class="{cell_class}" title="{title}">{display}</td>\n'
                    continue
                else:
                    cell_class = ''
                    display = str(action)
                html += f'                    <td class="{cell_class}">{display}</td>\n'
            else:
                html += f'                    <td class="empty">—</td>\n'
        html += '                </tr>\n'
    
    html += """            </tbody>
        </table>
        
        <h2>GOTO 表</h2>
        <table id="gotoTable">
            <thead>
                <tr>
                    <th class="state">状态</th>
"""
    
    # GOTO表头
    for nonterm in nonterminals:
        html += f'                    <th class="nonterminal">{nonterm}</th>\n'
    html += """                </tr>
            </thead>
            <tbody>
"""
    
    # GOTO表内容
    for state in states:
        html += f'                <tr>\n'
        html += f'                    <th class="state">{state}</th>\n'
        for nonterm in nonterminals:
            goto = goto_table.get((state, nonterm), '')
            if goto is not None and goto != '':
                html += f'                    <td class="goto">{goto}</td>\n'
            else:
                html += f'                    <td class="empty">—</td>\n'
        html += '                </tr>\n'
    
    html += """            </tbody>
        </table>
        
        <h2>产生式列表</h2>
        <table>
            <thead>
                <tr>
                    <th>编号</th>
                    <th>产生式</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # 产生式列表
    for idx, prod in enumerate(grammar.productions):
        left = prod.left
        right = ' '.join(prod.right) if prod.right else 'ε'
        html += f'                <tr>\n'
        html += f'                    <td>{idx}</td>\n'
        html += f'                    <td>{left} → {right}</td>\n'
        html += '                </tr>\n'
    
    html += """            </tbody>
        </table>
    </div>
    
    <script>
        function searchTable() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toUpperCase();
            const actionTable = document.getElementById('actionTable');
            const gotoTable = document.getElementById('gotoTable');
            
            [actionTable, gotoTable].forEach(table => {
                const rows = table.getElementsByTagName('tr');
                for (let i = 1; i < rows.length; i++) {
                    const cells = rows[i].getElementsByTagName('td');
                    const header = rows[i].getElementsByTagName('th')[0];
                    let found = false;
                    
                    if (header && header.textContent.toUpperCase().indexOf(filter) > -1) {
                        found = true;
                    }
                    
                    for (let j = 0; j < cells.length; j++) {
                        if (cells[j].textContent.toUpperCase().indexOf(filter) > -1) {
                            found = true;
                            break;
                        }
                    }
                    
                    rows[i].style.display = found ? '' : 'none';
                }
            });
        }
        
        function resetTable() {
            document.getElementById('searchInput').value = '';
            searchTable();
        }
    </script>
</body>
</html>
"""
    
    # 保存文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[OK] LALR(1)分析表已生成: {output_path}")
    return output_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="生成LALR(1)分析表的HTML可视化")
    parser.add_argument('config', help='文法配置文件路径')
    parser.add_argument('--output', '-o', help='输出HTML文件路径')
    
    args = parser.parse_args()
    
    output_file = generate_table_html(args.config, args.output)
    
    # 尝试在浏览器中打开
    import webbrowser
    try:
        webbrowser.open(f'file://{Path(output_file).absolute()}')
        print("已在浏览器中打开")
    except:
        print(f"请手动打开: {output_file}")


if __name__ == '__main__':
    main()
