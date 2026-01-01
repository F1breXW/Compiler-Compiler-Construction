from typing import List, Any

from driver.semantic_analyzer import SemanticAnalyzer
from driver import Symbol
from syntax import Production


class MySemanticAnalyzer(SemanticAnalyzer):
    """
    实现具体语义动作和中间代码生成的类
    """
    def __init__(self):
        super().__init__()


        self.current_type = None
        self.expr_type = None
        self.temp_vars = {}

        self.block_level = 0



    def semantic_action(self, production, symbols):
        """
        P -> S P
        P -> ε

        S -> E;
        S -> id := E ;
        S -> int id ;
        S -> { P }

        E -> E + T | E - T | T
        T -> T * F | T / F | F
        F -> ( E ) | id | num
        """
        prod_name = str(production)
        print(f"    [语义动作] 处理产生式：{prod_name}")
        left = production.left
        if left == 'P':
            return self.handle_program(production, symbols)
        elif left == 'S':
            return self.handle_statement(production, symbols)
        elif left == 'E':
            return self.handle_expression(production, symbols)
        elif left == 'T':
            return self.handle_term(production, symbols)
        elif left == 'F':
            return self.handle_factor(production, symbols)

        else:
            print(f"    [错误] 无效的产生式左部：{left}")
            return None

    def handle_program(self, production: Production, symbols: List[Symbol]) -> Any:
        if len(symbols) == 2: # P -> S P
            return True
        elif (len(symbols) == 0) or symbols[0] == 'ε': # P -> ε
            if self.block_level > 0:
                print(f"程序结束，但仍有{self.block_level}给未关闭的复合语句块")
            return None

    def handle_statement(self, production: Production, symbols: List[Symbol]) -> Any:
        prod_str = str(production)

        #if len(symbols) == 3 and str(symbols[0]) == '{' and str(symbols[2]) == '}':
        #    self.block_level += 1
        #    print(f"[语义操作] 进入复合语句块，层级：{self.block_level}")

        if "int id" in prod_str: # S -> int id ;
            type_token = symbols[0]
            id_sym = symbols[1]

            var_type = str(type_token.value)  # 'int'
            var_name = str(id_sym.value)

            if var_name in self.symbol_table:
                print(f"    [语义错误] 变量 '{var_name}' 重复声明")
                return None

            self.add_symbol(var_name, {"type": var_type, "initialized": False})
            print(f"    [语义] 声明变量: {var_name} : {var_type}")
            return True

        elif ":=" in prod_str: # S -> id := E ;
            # 赋值语句
            var_name = symbols[0].value
            expr_attr = symbols[2].attributes  # E的综合属性

            # 检查变量是否声明
            if var_name not in self.symbol_table:
                print(f"    [语义错误] 变量 '{var_name}' 未声明")
                return None

            # 获取变量类型
            var_info = self.symbol_table[var_name]

            # 检查表达式是否有属性
            if not expr_attr or "type" not in expr_attr:
                print(f"    [语义错误] 表达式属性缺失")
                return None

            # 检查类型匹配
            if var_info["type"] != expr_attr["type"]:
                print(f"    [语义错误] 类型不匹配: 不能将 {expr_attr['type']} 赋值给 {var_info['type']} 变量 {var_name}")
                return None

            # 生成中间代码
            if expr_attr.get("temp"):
                # 表达式结果在临时变量中
                self.emit(f"{var_name} := {expr_attr['temp']}")
            else:
                # 表达式是常量或变量
                self.emit(f"{var_name} := {expr_attr['value']}")

            # 标记变量已初始化
            var_info["initialized"] = True
            if expr_attr.get("temp"):
                print(f"    [语义] 赋值: {var_name} := {expr_attr.get('temp')}")
            else:
                print(f"    [语义] 赋值: {var_name} := {expr_attr.get('value')}")
            return True

        else:  # S → E ;
            # 表达式语句
            expr_attr = symbols[0].attributes
            if expr_attr and "temp" in expr_attr:
                # 表达式有结果，生成中间代码
                temp_var = expr_attr["temp"]
                print(f"    [语义] 表达式语句，结果在 {temp_var}")
            return True






    def handle_expression(self, production: Production, symbols: List[Symbol]) -> Any:
        """处理表达式: E → E + T | E - T | T"""
        prod_str = str(production)

        if len(symbols) == 1:  # E → T
            return symbols[0].attributes

        elif len(symbols) == 3:  # E → E op T
            left_attr = symbols[0].attributes
            op = symbols[1].value
            right_attr = symbols[2].attributes
            # 检查属性是否存在
            if not left_attr or "type" not in left_attr:
                print(f"    [语义错误] 左操作数属性缺失")
                return {"type": "error", "value": None}
            if not right_attr or "type" not in right_attr:
                print(f"    [语义错误] 右操作数属性缺失")
                return {"type": "error", "value": None}
            # 检查类型
            if left_attr["type"] != "int" or right_attr["type"] != "int":
                print(f"    [语义错误] 算术运算要求int类型，得到 {left_attr['type']} {op} {right_attr['type']}")
                return {"type": "error", "value": None}

            # 生成临时变量和中间代码
            temp_var = self.new_temp()

            left_val = left_attr.get("temp") or left_attr.get("value")
            right_val = right_attr.get("temp") or right_attr.get("value")

            self.emit(f"{temp_var} := {left_val} {op} {right_val}")

            # 记录临时变量类型
            self.temp_vars[temp_var] = "int"

            print(f"    [语义] 生成算术运算: {temp_var} = {left_val} {op} {right_val}")

            return {
                "type": "int",
                "temp": temp_var,
                "value": f"{left_val} {op} {right_val}"
            }

        return {"type": "error", "value": None}

    def handle_term(self, production: Production, symbols: List[Symbol]) -> Any:
        """处理项: T → T * F | T / F | F"""
        prod_str = str(production)

        if len(symbols) == 1:  # T → F
            return symbols[0].attributes

        elif len(symbols) == 3:  # T → T op F
            left_attr = symbols[0].attributes
            op = symbols[1].value
            right_attr = symbols[2].attributes
            # 检查属性是否存在
            if not left_attr or "type" not in left_attr:
                print(f"    [语义错误] 左操作数属性缺失")
                return {"type": "error", "value": None}
            if not right_attr or "type" not in right_attr:
                print(f"    [语义错误] 右操作数属性缺失")
                return {"type": "error", "value": None}
            # 检查类型
            if left_attr["type"] != "int" or right_attr["type"] != "int":
                print(f"    [语义错误] 算术运算要求int类型，得到 {left_attr['type']} {op} {right_attr['type']}")
                return {"type": "error", "value": None}


            # 生成临时变量和中间代码
            temp_var = self.new_temp()

            left_val = left_attr.get("temp") or left_attr.get("value")
            right_val = right_attr.get("temp") or right_attr.get("value")

            self.emit(f"{temp_var} := {left_val} {op} {right_val}")

            # 记录临时变量类型
            self.temp_vars[temp_var] = "int"

            print(f"    [语义] 生成项运算: {temp_var} = {left_val} {op} {right_val}")

            return {
                "type": "int",
                "temp": temp_var,
                "value": f"{left_val} {op} {right_val}"
            }

        return {"type": "error", "value": None}

    def handle_factor(self, production: Production, symbols: List[Symbol]) -> Any:
        """处理因子: F → (E) | id | num"""
        if len(symbols) == 3 and str(symbols[0].name) == '(':  # F → (E)
            return symbols[1].attributes

        elif len(symbols) == 1:
            sym = symbols[0]
            sym_name = str(sym.name)  # token类型：'num', 'id'
            sym_value = sym.value      # token值

            if sym_name == "num":  # 数字
                return {
                    "type": "int",
                    "value": sym_value,
                    "temp": None
                }



            elif sym_name == "id":  # 标识符
                var_name = str(sym_value)

                # 检查变量是否声明
                if var_name not in self.symbol_table:
                    print(f"    [语义错误] 变量 '{var_name}' 未声明")
                    return {"type": "error", "value": None}

                # 检查变量是否初始化
                var_info = self.symbol_table[var_name]
                if not var_info["initialized"]:
                    print(f"    [语义错误] 变量 '{var_name}' 可能未初始化")
                    return {"type": "error", "value": None}

                return {
                    "type": var_info["type"],
                    "value": var_name,
                    "temp": None
                }

        return {"type": "error", "value": None}



    def handle_type(self, production: Production, symbols: List[Symbol]) -> str:
        """处理类型: type → int | bool"""
        type_str = str(symbols[0])
        return type_str

