#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
综合测试脚本：测试所有高级测试程序
验证语义分析和中间代码生成功能
"""

import sys
import os
import io
from pathlib import Path

# Windows控制台编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from test_advanced import test_advanced_file


def main():
    """运行所有高级测试"""
    config_path = "configs/grammar_imperative.json"
    
    test_cases = [
        {
            "name": "类型检查和算术运算",
            "file": "test_programs/intermediate_code/advanced_test1.txt",
            "description": "测试变量声明、类型检查、算术表达式和运算符优先级"
        },
        {
            "name": "if/else语句",
            "file": "test_programs/intermediate_code/advanced_test2.txt",
            "description": "测试单分支if和双分支if-else的回填技术"
        },
        {
            "name": "while循环",
            "file": "test_programs/intermediate_code/advanced_test3.txt",
            "description": "测试while循环的回填和标签生成"
        },
        {
            "name": "复杂布尔表达式",
            "file": "test_programs/intermediate_code/advanced_test4.txt",
            "description": "测试&&、||逻辑运算符和复合条件"
        }
    ]
    
    print("=" * 80)
    print("语义分析和中间代码生成 - 综合测试")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for idx, test in enumerate(test_cases, 1):
        print(f"\n[测试 {idx}/4] {test['name']}")
        print(f"说明: {test['description']}")
        print("-" * 80)
        
        try:
            success = test_advanced_file(config_path, test['file'], verbose=False)
            if success:
                print(f"✓ 测试通过")
                passed += 1
            else:
                print(f"✗ 测试失败")
                failed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}")
            failed += 1
    
    # 输出汇总
    print("\n" + "=" * 80)
    print(f"测试汇总: 通过 {passed}/{len(test_cases)}, 失败 {failed}/{len(test_cases)}")
    print("=" * 80)
    
    if failed == 0:
        print("\n✓ 所有测试通过！语义分析和中间代码生成功能正常。")
        return 0
    else:
        print(f"\n✗ 有 {failed} 个测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
