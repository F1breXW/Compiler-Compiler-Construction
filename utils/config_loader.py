"""
文法配置加载器
实现配置文件的加载和解析，遵循单一职责原则
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os


@dataclass
class TestCase:
    """测试用例数据类"""
    input: str
    expected: str  # "legal" or "illegal"
    description: str = ""


@dataclass
class GrammarConfig:
    """
    文法配置数据类
    封装一个完整的编译器文法定义（词法+语法+测试）
    """
    name: str
    description: str
    lexical_rules: List[tuple]  # [(pattern, token), ...]
    grammar_rules: List[str]    # ["S -> E", "E -> E + T", ...]
    test_cases: List[TestCase]
    
    @property
    def terminals(self) -> List[str]:
        """从词法规则中提取终结符"""
        return [token for _, token in self.lexical_rules]


class ConfigLoader:
    """
    配置加载器
    职责：从JSON文件加载文法配置
    """
    
    def __init__(self, config_dir: str = "configs"):
        """
        初始化配置加载器
        
        参数:
            config_dir: 配置文件目录路径
        """
        self.config_dir = config_dir
        
    def load(self, filename: str) -> GrammarConfig:
        """
        加载单个文法配置文件
        
        参数:
            filename: 配置文件名（相对于config_dir）
        返回:
            GrammarConfig对象
        """
        filepath = os.path.join(self.config_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"配置文件不存在: {filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return self._parse_config(data)
    
    def load_all(self) -> List[GrammarConfig]:
        """
        加载配置目录下的所有文法配置
        
        返回:
            GrammarConfig对象列表
        """
        if not os.path.exists(self.config_dir):
            raise FileNotFoundError(f"配置目录不存在: {self.config_dir}")
            
        configs = []
        for filename in sorted(os.listdir(self.config_dir)):
            if filename.endswith('.json'):
                try:
                    config = self.load(filename)
                    configs.append(config)
                except Exception as e:
                    print(f"[警告] 加载配置文件 {filename} 失败: {e}")
                    
        return configs
    
    def _parse_config(self, data: Dict[str, Any]) -> GrammarConfig:
        """
        解析JSON数据为GrammarConfig对象
        
        参数:
            data: 从JSON文件读取的字典
        返回:
            GrammarConfig对象
        """
        # 解析词法规则
        lexical_rules = []
        for rule in data.get('lexical_rules', []):
            pattern = rule['pattern']
            token = rule['token']
            lexical_rules.append((pattern, token))
            
        # 解析语法规则
        grammar_rules = data.get('grammar_rules', [])
        
        # 解析测试用例
        test_cases = []
        for test in data.get('test_cases', []):
            test_case = TestCase(
                input=test['input'],
                expected=test['expected'],
                description=test.get('description', '')
            )
            test_cases.append(test_case)
            
        return GrammarConfig(
            name=data.get('name', 'Unknown'),
            description=data.get('description', ''),
            lexical_rules=lexical_rules,
            grammar_rules=grammar_rules,
            test_cases=test_cases
        )


class ConfigValidator:
    """
    配置验证器
    职责：验证配置的合法性
    """
    
    @staticmethod
    def validate(config: GrammarConfig) -> bool:
        """
        验证文法配置是否合法
        
        参数:
            config: 待验证的配置
        返回:
            True if valid, False otherwise
        """
        if not config.name:
            print("[错误] 文法名称不能为空")
            return False
            
        if not config.lexical_rules:
            print("[错误] 词法规则不能为空")
            return False
            
        if not config.grammar_rules:
            print("[错误] 语法规则不能为空")
            return False
            
        # 验证语法规则格式
        for rule in config.grammar_rules:
            if '->' not in rule:
                print(f"[错误] 语法规则格式错误: {rule}")
                return False
                
        return True
