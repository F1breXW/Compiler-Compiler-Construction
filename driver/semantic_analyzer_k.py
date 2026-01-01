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

        self.label_counter = 0
        self.backpatch_list=[]
        self.control_stack=[]
        self.while_stack = []
        self.current_type = None
        self.expr_type = None
        self.temp_vars = {}

        self.bool_expr_temp = None

        self.block_level = 0

    def new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit_with_backpatch(self, code: str, patch_list=None) -> int:
        addr = self.nextinstr
        self.emit(code)
        if patch_list is not None:
            patch_list.append(addr)

        return addr

    def make_list(self, addr: int):
        return [addr]

    def merge(self, list1, list2):
        return list1+list2

    def backpatch(self, patch_list, label):
        if not patch_list:
            return
        for addr in patch_list:
            if addr < len(self.intermediate_code):
                code = self.intermediate_code[addr]
                if code.startswith("if ") and " goto" in code:
                    parts = code.split(" goto ")
                    if len(parts)==2:
                        self.intermediate_code[addr] = f"{parts[0]} goto {label}"
                elif code.startswith("goto "):
                    self.intermediate_code[addr] = f"goto {label}"

    def semantic_action(self, production, symbols):
        """
        P -> S P
        P -> ε

        S -> E;
        S -> id := E ;
        S -> type id ;
        S -> if ( B ) then S
        S -> if ( B ) then S else S
        S -> while ( B ) do S
        S -> { P }

        B -> E relop E
        B -> true | false
        B -> ( B )
        B -> ! B
        B -> B && B
        B -> B || B

        E -> E + T | E - T | T
        T -> T * F | T / F | F
        F -> ( E ) | id | num

        relop -> == | != | < | > | <= | >=

        type -> int | bool
        """
        prod_name = str(production)
        print(f"[语义动作]处理产生式：{prod_name}")
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
        elif left == 'B':
            return  self.handle_boolean(production, symbols)
        else:
            print(f"[错误] 无效的产生式左部：{left}")
            return None

    def handle_program(self, production: Production, symbols: List[Symbol]) -> Any:
        if len(symbols) == 2: # P -> S P
            return None
        elif (len(symbols) == 0) or symbols[0] == 'ε': # P -> ε
            if self.block_level > 0:
                print(f"程序结束，但仍有{self.block_level}给未关闭的复合语句块")
            return None

    def handle_statement(self, production: Production, symbols: List[Symbol]) -> Any:
        prod_str = str(production)

        #if len(symbols) == 3 and str(symbols[0]) == '{' and str(symbols[2]) == '}':
        #    self.block_level += 1
        #    print(f"[语义操作] 进入复合语句块，层级：{self.block_level}")

        if ("int id" in prod_str or "bool id" in prod_str): # S -> int id ; | S -> bool id ;
            type_token = symbols[0]
            id_sym = symbols[1]

            var_type = str(type_token.value)  # 'int' 或 'bool'
            var_name = str(id_sym.value)

            if var_name in self.symbol_table:
                print(f"[语义错误] 变量 '{var_name}' 重复声明")
                return None

            self.add_symbol(var_name, {"type": var_type, "initialized": False})
            print(f"[语义] 声明变量: {var_name} : {var_type}")
            return None

        elif ":=" in prod_str: # S -> id := E ;
            # 赋值语句
            var_name = symbols[0].value
            expr_attr = symbols[2].attributes  # E的综合属性

            # 检查变量是否声明
            if var_name not in self.symbol_table:
                print(f"[语义错误] 变量 '{var_name}' 未声明")
                return None

            # 获取变量类型
            var_info = self.symbol_table[var_name]

            # 检查表达式是否有属性
            if not expr_attr or "type" not in expr_attr:
                print(f"[语义错误] 表达式属性缺失")
                return None

            # 检查类型匹配
            if var_info["type"] != expr_attr["type"]:
                print(f"[语义错误] 类型不匹配: 不能将 {expr_attr['type']} 赋值给 {var_info['type']} 变量 {var_name}")
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
            print(f"[语义] 赋值: {var_name} := {expr_attr.get('value', expr_attr.get('temp', '?'))}")
            return None

        elif "if" in prod_str:
            # if语句处理
            return self.handle_if_statement(production, symbols)

        elif "while" in prod_str:
            # while语句处理
            return self.handle_while_statement(production, symbols)

        #elif str(symbols[-1]) == '}':
        #    # 复合语句结束
        #    self.block_level -= 1
        #    print(f"[语义] 退出复合语句块，层级: {self.block_level}")
        #    return None

        else:  # S → E ;
            # 表达式语句
            expr_attr = symbols[0].attributes
            if expr_attr and "temp" in expr_attr:
                # 表达式有结果，生成中间代码
                temp_var = expr_attr["temp"]
                print(f"[语义] 表达式语句，结果在 {temp_var}")
            return None

    def handle_if_statement(self, production: Production, symbols: List[Symbol]) -> Any:
        """处理if语句"""
        bool_attr = symbols[2].attributes  # B的综合属性
        prod_str = str(production)

        if "else" in prod_str:  # S → if (B) then S else S
            then_label = self.new_label()
            else_label = self.new_label()
            end_label = self.new_label()

            self.backpatch(bool_attr["truelist"], then_label)
            skip_else_addr = self.emit_with_backpatch(f"goto L")
            self.emit(f"LABEL {then_label}:")

            self.emit(f"goto {end_label}")
            self.emit(f"LABEL {else_label}:")
            self.backpatch([skip_else_addr], else_label)

            self.emit(f"LABEL {end_label}")
            return None

        else:  # S → if (B) then S
            then_label = self.new_label()
            self.backpatch(bool_attr["truelist"], then_label)
            self.emit(f"LABEL {then_label}")
            return {"nextlist": bool_attr.get("falselist", [])}

    def handle_while_statement(self, production: Production, symbols: List[Symbol]) -> Any:
        """处理while语句: S → while (B) do S"""
        bool_attr = symbols[2].attributes  # B的综合属性

        if not bool_attr:
            print(f"[语义错误] while语句中布尔表达式属性缺失")
            return None

        # 生成标签
        begin_label = self.new_label()
        body_label = self.new_label()
        end_label = self.new_label()

        # 保存标签信息，供break/continue使用
        self.while_stack.append({
            "cond_label": begin_label,
            "end_label": end_label
        })

        # 生成代码
        self.emit(f"LABEL {begin_label}:")
        # 回填truelist到循环体开始
        self.backpatch(bool_attr.get("truelist", []), body_label)
        self.emit(f"LABEL {body_label}:")
        # 循环体结束后跳回条件判断
        self.emit(f"goto {begin_label}")
        # falselist跳到循环结束
        self.emit(f"LABEL {end_label}:")
        self.backpatch(bool_attr.get("falselist", []), end_label)

        print(f"[语义] 生成while语句，标签: {begin_label}, {body_label}, {end_label}")
        return None

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
                print(f"[语义错误] 左操作数属性缺失")
                return {"type": "error", "value": None}
            if not right_attr or "type" not in right_attr:
                print(f"[语义错误] 右操作数属性缺失")
                return {"type": "error", "value": None}
            # 检查类型
            if left_attr["type"] != "int" or right_attr["type"] != "int":
                print(f"[语义错误] 算术运算要求int类型，得到 {left_attr['type']} {op} {right_attr['type']}")
                return {"type": "error", "value": None}

            # 生成临时变量和中间代码
            temp_var = self.new_temp()

            left_val = left_attr.get("temp") or left_attr.get("value")
            right_val = right_attr.get("temp") or right_attr.get("value")

            self.emit(f"{temp_var} := {left_val} {op} {right_val}")

            # 记录临时变量类型
            self.temp_vars[temp_var] = "int"

            print(f"[语义] 生成算术运算: {temp_var} = {left_val} {op} {right_val}")

            return {
                "type": "int",
                "temp": temp_var,
                "value": None
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
                print(f"[语义错误] 左操作数属性缺失")
                return {"type": "error", "value": None}
            if not right_attr or "type" not in right_attr:
                print(f"[语义错误] 右操作数属性缺失")
                return {"type": "error", "value": None}
            # 检查类型
            if left_attr["type"] != "int" or right_attr["type"] != "int":
                print(f"[语义错误] 算术运算要求int类型，得到 {left_attr['type']} {op} {right_attr['type']}")
                return {"type": "error", "value": None}


            # 生成临时变量和中间代码
            temp_var = self.new_temp()

            left_val = left_attr.get("temp") or left_attr.get("value")
            right_val = right_attr.get("temp") or right_attr.get("value")

            self.emit(f"{temp_var} := {left_val} {op} {right_val}")

            # 记录临时变量类型
            self.temp_vars[temp_var] = "int"

            print(f"[语义] 生成项运算: {temp_var} = {left_val} {op} {right_val}")

            return {
                "type": "int",
                "temp": temp_var,
                "value": None
            }

        return {"type": "error", "value": None}

    def handle_factor(self, production: Production, symbols: List[Symbol]) -> Any:
        """处理因子: F → (E) | id | num"""
        if len(symbols) == 3 and str(symbols[0].name) == '(':  # F → (E)
            return symbols[1].attributes

        elif len(symbols) == 1:
            sym = symbols[0]
            sym_name = str(sym.name)  # token类型：'num', 'id', 'true', 'false'
            sym_value = sym.value      # token值

            if sym_name == "num":  # 数字
                return {
                    "type": "int",
                    "value": sym_value,
                    "temp": None
                }

            elif sym_name in ["true", "false"]:  # 布尔常量
                return {
                    "type": "bool",
                    "value": sym_name == "true",
                    "temp": None
                }

            elif sym_name == "id":  # 标识符
                var_name = str(sym_value)

                # 检查变量是否声明
                if var_name not in self.symbol_table:
                    print(f"[语义错误] 变量 '{var_name}' 未声明")
                    return {"type": "error", "value": None}

                # 检查变量是否初始化
                var_info = self.symbol_table[var_name]
                if not var_info["initialized"]:
                    print(f"[语义警告] 变量 '{var_name}' 可能未初始化")

                return {
                    "type": var_info["type"],
                    "value": var_name,
                    "temp": None
                }

        return {"type": "error", "value": None}

    def handle_boolean(self, production: Production, symbols: List[Symbol]) -> Any:
        """处理布尔表达式 - 生成回填列表"""
        prod_str = str(production)

        # B -> E relop E (relop = ==, !=, <, >, <=, >=)
        if len(symbols) == 3 and symbols[0].attributes and symbols[2].attributes:
            if symbols[0].attributes.get("type") == "int" and symbols[2].attributes.get("type") == "int":
                # 这是关系比较表达式 B -> E relop E
                E1_attr = symbols[0].attributes
                relop = str(symbols[1].value)  # 直接使用运算符符号
                E2_attr = symbols[2].attributes

                # 获取操作数（优先使用temp，如果没有则使用value）
                left_val = E1_attr.get('temp') if E1_attr.get('temp') else E1_attr.get('value')
                right_val = E2_attr.get('temp') if E2_attr.get('temp') else E2_attr.get('value')

                # 生成条件跳转指令
                code = f"if {left_val} {relop} {right_val} goto L"

                # 生成跳转为真的指令（地址待回填）
                truelist = self.make_list(self.emit_with_backpatch(code))

                # 生成跳转为假的指令（无条件跳转，地址待回填）
                falselist = self.make_list(self.emit_with_backpatch("goto L"))

                return {
                    "type": "bool",
                    "truelist": truelist,
                    "falselist": falselist
                }

        if symbols[0].name in ['true', 'false']:  # B → true | false
            value = symbols[0].value

            if value == 'true':
                # 总是为真，只有truelist
                return {
                    "type": "bool",
                    "truelist": self.make_list(self.emit_with_backpatch("goto L")),
                    "falselist": []
                }
            else:  # false
                # 总是为假，只有falselist
                return {
                    "type": "bool",
                    "truelist": [],
                    "falselist": self.make_list(self.emit_with_backpatch("goto L"))
                }

        elif len(symbols) == 2 and symbols[0].name == '!':  # B → ! B1
            B1_attr = symbols[1].attributes
            # 交换truelist和falselist
            return {
                "type": "bool",
                "truelist": B1_attr.get("falselist", []),
                "falselist": B1_attr.get("truelist", [])
            }

        elif len(symbols) == 3 and symbols[1].name in ['&&', '||']:  # B → B1 && B2 | B1 || B2
            B1_attr = symbols[0].attributes
            op = symbols[1].value
            B2_attr = symbols[2].attributes

            if op == '&&':
                # B1为真时，需要回填到B2开始处
                then_label = self.new_label()
                self.backpatch(B1_attr.get("truelist", []), then_label)
                self.emit(f"LABEL {then_label}:")

                # 合并B1.falselist和B2.falselist
                falselist = self.merge(B1_attr.get("falselist", []), B2_attr.get("falselist", []))

                return {
                    "type": "bool",
                    "truelist": B2_attr.get("truelist", []),
                    "falselist": falselist
                }

            elif op == '||':
                # B1为假时，需要回填到B2开始处
                else_label = self.new_label()
                self.backpatch(B1_attr.get("falselist", []), else_label)
                self.emit(f"LABEL {else_label}:")

                # 合并B1.truelist和B2.truelist
                truelist = self.merge(B1_attr.get("truelist", []), B2_attr.get("truelist", []))

                return {
                    "type": "bool",
                    "truelist": truelist,
                    "falselist": B2_attr.get("falselist", [])
                }

        return {"type": "bool", "truelist": [], "falselist": []}

    def handle_type(self, production: Production, symbols: List[Symbol]) -> str:
        """处理类型: type → int | bool"""
        type_str = str(symbols[0])
        return type_str

    def handle_relop(self, production: Production, symbols: List[Symbol]) -> Any:
        """处理关系操作符: relop → == | != | < | > | <= | >="""
        op_str = str(symbols[0].value)
        return {"op": op_str}