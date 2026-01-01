from .thompson import ThompsonConstructor
from .nfa import NFA

class RegexParser:
    """
    简单的正则表达式解析器
    支持的操作符:
    - 连接: ab
    - 选择: a|b
    - 闭包: a*
    - 正闭包: a+
    - 括号: (a|b)
    - 字符类: [a-z] (仅支持简单范围)
    """
    
    def __init__(self, thompson: ThompsonConstructor):
        self.thompson = thompson
        self.pos = 0
        self.regex = ""
        
    def parse(self, regex: str, tag: str = None) -> NFA:
        """解析正则表达式并返回NFA"""
        self.regex = regex
        self.pos = 0
        nfa = self._parse_expression()
        
        # 设置接受状态的标签
        if tag:
            for state in nfa.accept_states:
                state.tag = tag
        return nfa
        
    def _peek(self) -> str:
        if self.pos < len(self.regex):
            return self.regex[self.pos]
        return ""
        
    def _match(self, char: str) -> bool:
        if self._peek() == char:
            self.pos += 1
            return True
        return False
        
    def _parse_expression(self) -> NFA:
        """expression -> term ('|' term)*"""
        nfa = self._parse_term()
        
        while self._match('|'):
            nfa2 = self._parse_term()
            nfa = self.thompson.construct_union(nfa, nfa2)
            
        return nfa
        
    def _parse_term(self) -> NFA:
        """term -> factor*"""
        nfa = None
        
        while True:
            char = self._peek()
            if not char or char == '|' or char == ')':
                break
                
            next_nfa = self._parse_factor()
            if nfa is None:
                nfa = next_nfa
            else:
                nfa = self.thompson.construct_concat(nfa, next_nfa)
                
        return nfa if nfa else self.thompson.construct_simple("", "") # Empty string NFA?
        
    def _parse_factor(self) -> NFA:
        """factor -> atom ('*' | '+')?"""
        nfa = self._parse_atom()
        
        if self._match('*'):
            nfa = self.thompson.construct_star(nfa)
        elif self._match('+'):
            nfa = self.thompson.construct_plus(nfa)
            
        return nfa
        
    def _parse_atom(self) -> NFA:
        """atom -> char | '(' expr ')' | '[' range ']' """
        char = self._peek()
        
        if self._match('('):
            nfa = self._parse_expression()
            if not self._match(')'):
                raise ValueError(f"Missing closing parenthesis at {self.pos}")
            return nfa
            
        if self._peek() == '[':
            return self._parse_bracket()
            
        # 普通字符
        self.pos += 1
        # 处理转义字符
        if char == '\\':
            char = self.regex[self.pos]
            self.pos += 1
            
        return self.thompson.construct_char(char)

    def _parse_bracket(self) -> NFA:
        """解析 [...]"""
        self._match('[')
        nfa = None
        
        while self._peek() != ']':
            if self.pos >= len(self.regex):
                raise ValueError("Unclosed character class")
                
            start = self.regex[self.pos]
            self.pos += 1
            
            # Check for range a-z
            if self._peek() == '-':
                self.pos += 1 # consume '-'
                if self.pos >= len(self.regex):
                     raise ValueError("Invalid range in character class")
                end = self.regex[self.pos]
                self.pos += 1
                part_nfa = self.thompson.construct_range(start, end)
            else:
                part_nfa = self.thompson.construct_char(start)
                
            if nfa is None:
                nfa = part_nfa
            else:
                nfa = self.thompson.construct_union(nfa, part_nfa)
        
        self._match(']')
        return nfa
