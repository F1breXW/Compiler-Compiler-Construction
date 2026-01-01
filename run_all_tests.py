#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整项目测试脚本 - 一键运行所有测试
"""

import os
import sys
import io
import subprocess
from pathlib import Path

# Windows控制台UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    os.system('chcp 65001 >nul 2>&1')

def run_test(config, source, description):
    """运行单个测试"""
    print(f"\n{'='*70}")
    print(f"[测试] {description}")
    print(f"{'='*70}")
    
    cmd = f'python test_from_file.py {config} {source}'
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 查找关键输出
        output = result.stdout + result.stderr
        
        if '[分析结果] 合法语句' in output:
            print("[PASS] 测试通过 - 源程序合法")
            
            # 查找产生式序列
            if '[产生式序列]' in output:
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if '[产生式序列]' in line:
                        print(f"\n{line}")
                        # 打印后续几行
                        for j in range(1, min(6, len(lines)-i)):
                            if lines[i+j].strip() and not lines[i+j].startswith('['):
                                print(lines[i+j])
                            if lines[i+j].startswith('['):
                                break
                        break
            
            # 查找中间代码
            if '[生成代码]' in output:
                print("\n[中间代码生成]:")
                count = 0
                for line in output.split('\n'):
                    if '[生成代码]' in line:
                        count += 1
                        code = line.split('[生成代码]')[1].strip()
                        print(f"  {count}. {code}")
            
            return True
        else:
            print("[FAIL] 测试失败")
            return False
            
    except Exception as e:
        print(f"[ERROR] 测试出错: {e}")
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║        编译器-编译器项目 - 完整测试套件                        ║
║                                                                ║
║  第一部分: 词法和语法分析（自动生成）                           ║
║  第二部分: 中间代码生成                                        ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    print("\n" + "="*70)
    print("第一部分: 自动生成词法和语法分析器测试")
    print("="*70)
    
    # 文法1测试
    print("\n【文法1: 算术表达式文法】")
    results.append(run_test(
        "configs/grammar1_arithmetic.json",
        "test_programs/arithmetic_1.txt",
        "算术表达式 - 测试1: id + id * id"
    ))
    
    results.append(run_test(
        "configs/grammar1_arithmetic.json",
        "test_programs/arithmetic_2.txt",
        "算术表达式 - 测试2: ( id + id ) * id"
    ))
    
    # 文法2测试
    print("\n【文法2: 赋值语句文法】")
    results.append(run_test(
        "configs/grammar2_assignment.json",
        "test_programs/assignment_1.txt",
        "赋值语句 - 测试1: x := id + id"
    ))
    
    results.append(run_test(
        "configs/grammar2_assignment.json",
        "test_programs/assignment_2.txt",
        "赋值语句 - 测试2: result := id - num"
    ))
    
    print("\n" + "="*70)
    print("第二部分: 中间代码生成测试")
    print("="*70)
    
    print("\n【文法3: 简化命令式语言（用于中间代码生成）】")
    results.append(run_test(
        "configs/grammar_simple_ic.json",
        "test_programs/intermediate_code/ic_test1.txt",
        "中间代码 - 测试1: 算术表达式"
    ))
    
    results.append(run_test(
        "configs/grammar_simple_ic.json",
        "test_programs/intermediate_code/ic_test2.txt",
        "中间代码 - 测试2: 复杂表达式"
    ))
    
    results.append(run_test(
        "configs/grammar_simple_ic.json",
        "test_programs/intermediate_code/ic_test3.txt",
        "中间代码 - 测试3: 括号表达式"
    ))
    
    # 汇总结果
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n第一部分（自动生成）: {sum(results[:4])}/4 通过")
    print(f"第二部分（中间代码）: {sum(results[4:])}/3 通过")
    print(f"\n总体通过率: {passed}/{total} ({100*passed/total:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！项目满足课程要求。")
    else:
        print(f"\n[WARNING] {total - passed} 个测试失败")
    
    print("\n" + "="*70)
    print("生成的文件:")
    print("="*70)
    print("  - generated/*.json         (语法树JSON)")
    print("  - generated/*_ir.txt       (中间代码)")
    print("  - visualizations/*.dot     (语法树可视化)")
    print("  - visualizations/*.html    (分析表可视化)")
    print("\n详细测试报告请查看: TEST_REPORT.md")
    print("="*70)

if __name__ == '__main__':
    main()
