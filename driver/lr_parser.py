"""
LR分析器驱动程序
"""

from typing import List, Dict, Tuple, Callable, Optional, Any
from syntax import Grammar
from .symbol import Symbol


class LRParser:
    """
    LR分析器驱动程序
    实现基于栈的LR分析，并提供语义动作接口
    """
    
    def __init__(self, 
                 grammar: Grammar, 
                 action_table: Dict[Tuple[int, str], Tuple[str, int]], 
                 goto_table: Dict[Tuple[int, str], int],
                 semantic_handler: Optional[Callable] = None):
        """
        初始化LR分析器
        
        参数:
            grammar: 文法对象
            action_table: ACTION表 {(state, terminal): (action, value)}
            goto_table: GOTO表 {(state, non_terminal): next_state}
            semantic_handler: 语义动作处理器(可选)
        """
        self.grammar = grammar
        self.action_table = action_table
        self.goto_table = goto_table
        self.semantic_handler = semantic_handler
        
        # 分析栈: 存储(状态, 符号)对
        self.state_stack: List[int] = []
        self.symbol_stack: List[Symbol] = []
        
        # 分析历史记录(用于调试和演示)
        self.parse_history: List[Dict] = []
    
    def parse(self, tokens: List[Tuple[str, Any]]) -> bool:
        """
        LR分析主函数
        
        算法原理(LR分析算法):
        1. 初始化: 状态栈压入起始状态0
        2. 重复以下步骤:
           a) 读取当前输入符号a
           b) 查ACTION[当前状态, a]:
              - shift s: 压入状态s和符号a，前进输入指针
              - reduce A->β: 弹出|β|个状态，查GOTO[栈顶状态, A]，压入
              - accept: 分析成功
              - error: 分析失败
        
        参数:
            tokens: 输入token序列，格式[(token_type, token_value), ...]
        
        返回: True表示分析成功，False表示失败
        """
        print("\n" + "="*60)
        print("开始LR分析")
        print("="*60)
        
        # 初始化
        self.state_stack = [0]
        self.symbol_stack = []
        self.parse_history = []
        
        # 添加结束标记
        tokens = tokens + [('$', None)]
        input_index = 0
        
        step = 0
        while True:
            step += 1
            current_state = self.state_stack[-1]
            current_token, current_value = tokens[input_index]
            
            # 打印当前状态
            self._print_step(step, current_state, current_token, input_index, tokens)
            
            # 查ACTION表
            action_key = (current_state, current_token)
            if action_key not in self.action_table:
                print(f"\n[错误] 语法错误: 状态{current_state}无法处理输入'{current_token}'")
                return False
            
            action, value = self.action_table[action_key]
            
            if action == 'shift':
                self._handle_shift(value, current_token, current_value, step)
                input_index += 1
            
            elif action == 'reduce':
                if not self._handle_reduce(value, step):
                    return False
            
            elif action == 'accept':
                print(f"  动作: ACCEPT")
                print("\n" + "="*60)
                print("分析成功!")
                print("="*60)
                return True
            
            else:
                print(f"\n[错误] 未知动作: {action}")
                return False
    
    def _handle_shift(self, state: int, token: str, value: Any, step: int):
        """处理shift动作"""
        print(f"  动作: SHIFT {state}")
        self.state_stack.append(state)
        self.symbol_stack.append(Symbol(token, value))
        
        # 记录历史
        self.parse_history.append({
            'step': step,
            'action': 'shift',
            'state': state,
            'symbol': token
        })
    
    def _handle_reduce(self, prod_id: int, step: int) -> bool:
        """处理reduce动作"""
        production = self.grammar.productions[prod_id]
        print(f"  动作: REDUCE {production}")
        
        # 弹出|β|个状态和符号
        beta_length = len(production.right)
        if production.right == ('ε',):
            beta_length = 0
        
        # 保存归约前的符号栈(用于语义动作)
        reduced_symbols = []
        for _ in range(beta_length):
            self.state_stack.pop()
            reduced_symbols.insert(0, self.symbol_stack.pop())
        
        # 调用语义动作处理器
        semantic_value = self._handle_semantic_action(production, reduced_symbols)
        
        # 查GOTO表
        goto_state = self.state_stack[-1]
        goto_key = (goto_state, production.left)
        
        if goto_key not in self.goto_table:
            print(f"\n[错误] GOTO表错误: 状态{goto_state}无法处理非终结符'{production.left}'")
            return False
        
        next_state = self.goto_table[goto_key]
        self.state_stack.append(next_state)
        self.symbol_stack.append(Symbol(production.left, semantic_value))
        
        print(f"  GOTO 状态{next_state}")
        
        # 记录历史
        self.parse_history.append({
            'step': step,
            'action': 'reduce',
            'production': str(production),
            'goto': next_state
        })
        
        return True
    
    def _handle_semantic_action(self, production, symbols: List[Symbol]) -> Any:
        """
        处理语义动作 - 预留给同学B的接口
        
        参数:
            production: 使用的产生式
            symbols: 归约的符号序列(从左到右)
        
        返回: 该非终结符的语义值
        """
        print(f"    [语义动作] 产生式: {production}")
        print(f"    [语义动作] 归约符号: {[s.name + ':' + str(s.value) for s in symbols]}")
        
        # 如果用户提供了语义处理器，调用它
        if self.semantic_handler is not None:
            result = self.semantic_handler(production, symbols)
            print(f"    [语义动作] 返回值: {result}")
            return result
        
        # 默认行为: 简单传递第一个符号的值
        if symbols:
            return symbols[0].value
        return None
    
    def _print_step(self, step: int, state: int, token: str, index: int, tokens: List):
        """打印分析步骤信息"""
        print(f"\n步骤 {step}:")
        print(f"  状态栈: {self.state_stack}")
        print(f"  符号栈: {[s.name for s in self.symbol_stack]}")
        print(f"  当前状态: {state}")
        print(f"  当前输入: {token} (位置{index})")
        print(f"  剩余输入: {[t[0] for t in tokens[index:]]}")
    
    def get_parse_tree(self) -> Dict:
        """
        获取分析树(可选功能)
        返回分析历史记录，可用于可视化
        """
        return {
            'history': self.parse_history,
            'success': len(self.parse_history) > 0 and 
                      self.parse_history[-1].get('action') == 'accept'
        }
