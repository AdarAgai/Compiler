from utils import *


class QuadGenerator:
    def __init__(self, symbol_table):
        self.temp_var_count = 0
        self.temp_label_count = 0
        self.symbol_table = symbol_table

    def generate_assignment_stmt(self, p):

        variable_type = self.symbol_table.get_type(p.ID)
        expression_type = self.get_expression_type(p.expression.value)

        if variable_type == INT and expression_type == INT:
            return f"{IASN} {p.ID} {p.expression.value}"

        elif variable_type == FLOAT and expression_type == FLOAT:
            return f"{RASN} {p.ID} {p.expression.value}"

        elif variable_type == FLOAT and expression_type == INT:
            temp_var = self.generate_temp_var()
            conversion_code = self.generate_conversion(
                INT, p.expression.value, temp_var
            )
            assignment_code = f"{RASN} {p.ID} {self.temp_var_count}\n"
            return f"{conversion_code}\n{assignment_code}"
        else:
            print(f"Error: Type mismatch on line {p.lineno}.", file=sys.stderr)
            raise Exception("Type mismatch")

    def generate_conversion(self, source_type, source_value, temp_var):
        if source_type == INT:
            return f"{ITOR} {temp_var} {source_value}.0"
        elif source_type == FLOAT:
            int_value = source_value.split(".")[0]
            return f"{RTOI} {temp_var} {int_value}"
        return None

    def get_expression_value_type(self, expression_value):
        if expression_value.isdigit():
            return INT
        elif expression_value.replace(".", "", 1).isdigit():
            return FLOAT
        else:
            return self.symbol_table.get_type(expression_value)

    def generate_temp_var(self):
        self.temp_var_count += 1
        return f"var_temp{self.temp_var_count}"

    def generate_temp_label(self):
        self.temp_label_count += 1
        return f"label_temp{self.temp_label_count}"

    def generate_input_stmt(self, p):
        if self.symbol_table.get(p.ID) == INT:
            return f"{IINP} {p.ID}"
        else:
            return f"{RINP} {p.ID}"

    def generate_output_stmt(self, p):
        if self.symbol_table.get_type(p.ID) == INT:
            return f"{IPRT} {p.ID}"
        else:
            return f"{RPRT} {p.ID}"

    def generate_if_stmt(self, p, if_code, else_code):
        else_label = self.generate_temp_label()
        end_label = self.generate_temp_label()
        code = ""
        code += f"{p.boolexpr.code}\n"
        code += f"{JMPZ} {else_label} {p.boolexpr.value}\n"
        code += f"{if_code}\n"
        code += f"{JUMP} {end_label}\n"
        code += f"{else_label}: {else_code}\n"
        code += f"{end_label}:\n"
        return code

    def generate_while_stmt(self, p):
        start_label = self.generate_temp_label()
        end_label = self.generate_temp_label()
        code = ""
        code += f"{start_label}:\n"
        code += f"{p.boolexpr.code}\n"
        code += f"{JMPZ} {end_label} {p.boolexpr.value}\n"
        code += f"{p.stmt.code}\n"
        code += f"{JUMP} {start_label}\n"
        code += f"{end_label}:\n"
        return code

    def generate_or(self, p):
        end_label = self.generate_temp_label()
        false_label = self.generate_temp_label()
        or_result_var = self.generate_temp_var()

        code = ""
        code += f"{p.boolexpr.code}"
        code += f"{JUMPZ} {false_label} {p.boolexpr.value}\n"
        code += f"{IASN} {or_result_var} 1\n"
        code += f"{JUMP} {end_label}\n"
        code += f"{false_label}: {p.boolterm.code}\n"
        code += f"{JUMPZ} {false_label} {p.boolterm.value}\n"
        code += f"{IASN} {or_result_var} 1\n"
        code += f"{end_label}:\n"

        return code, or_result_var

    def generate_and(self, p):
        end_label = self.generate_temp_label()
        false_label = self.generate_temp_label()
        and_result_var = self.generate_temp_var()

        code = ""
        code += f"{p.boolexpr.code}"
        code += f"{JUMPZ} {false_label} {p.boolterm.value}\n"
        code += f"{p.boolfactor.code}\n"
        code += f"{JUMPZ} {false_label} {p.boolfactor.value}\n"
        code += f"{IASN} {and_result_var} 1\n"
        code += f"{JUMP} {end_label}\n"
        code += f"{false_label}: {IASN} {and_result_var} 0\n"
        code += f"{end_label}:\n"

        return code, and_result_var

    def generate_not(self, p):
        not_result_var = self.generate_temp_var()

        code = ""
        code += f"{p.boolexpr.code}\n"
        code += f"{IEQL} {not_result_var} {p.boolexpr.value} 0\n"

        return code, not_result_var

    def generate_relop(self, p):
        relop_result_var = self.variable_generator.get_new_int_variable()

        expression0_type = self.get_expression_type(p.expression0.value)
        expression1_type = self.get_expression_type(p.expression1.value)

        generated_code = f"{p.expression0.code}\n{p.expression1.code}\n"

        if expression1_type == FLOAT and expression0_type == INT:
            temp_var = self.variable_generator.get_new_float_variable()
            generated_code += (
                self.generate_conversion(INT, p.expression0.value, temp_var) + "\n"
            )
            expression0_value = temp_var
            expression0_type = FLOAT
        elif expression1_type == INT and expression0_type == FLOAT:
            temp_var = self.variable_generator.get_new_float_variable()
            generated_code += (
                self.generate_conversion(INT, p.expression1.value, temp_var) + "\n"
            )
            expression1_value = temp_var
            expression1_type = FLOAT

        if expression0_type == FLOAT and expression1_type == FLOAT:
            if relop == EQUAL:
                generated_code += (
                    f"REQL {relop_result_var} {expression0_value} {expression1_value}"
                )
            elif relop == NOT_EQUAL:
                generated_code += (
                    f"RNQL {relop_result_var} {expression0_value} {expression1_value}"
                )
            elif relop == LESS_THAN:
                generated_code += (
                    f"RLSS {relop_result_var} {expression0_value} {expression1_value}"
                )
            elif relop == GREATER_THAN:
                generated_code += (
                    f"RGRT {relop_result_var} {expression0_value} {expression1_value}"
                )
            elif relop == LESS_THAN_EQUAL:
                temp_var = self.variable_generator.get_new_float_variable()
                generated_code += (
                    f"RGRT {relop_result_var} {expression0_value} {expression1_value}\n"
                )
                generated_code += f"REQL {relop_result_var} {temp_var} 0"
            elif relop == GREATER_THAN_EQUAL:
                temp_var = self.variable_generator.get_new_float_variable()
                generated_code += (
                    f"RLSS {relop_result_var} {expression0_value} {expression1_value}\n"
                )
                generated_code += f"REQL {relop_result_var} {temp_var} 0"
            else:
                print(
                    f"Error: Unsupported relational operator for floats: {relop}.",
                    file=sys.stderr,
                )
                raise Exception(f"Unsupported relational operator for floats: {relop}")

        elif expr1_type == INT and expr2_type == INT:
            if relop == "==":
                generated_code += (
                    f"IEQL {relop_result_var} {expression0_value} {expression1_value}"
                )
            elif relop == "!=":
                generated_code += (
                    f"INQL {relop_result_var} {expression0_value} {expression1_value}"
                )
            elif relop == "<":
                generated_code += (
                    f"ILSS {relop_result_var} {expression0_value} {expression1_value}"
                )
            elif relop == ">":
                generated_code += (
                    f"IGRT {relop_result_var} {expression0_value} {expression1_value}"
                )
            elif relop == "<=":
                temp_var = self.variable_generator.get_new_int_variable()
                generated_code += (
                    f"IGRT {temp_var} {expression0_value} {expression1_value}\n"
                )
                generated_code += f"IEQL {relop_result_var} {temp_var} 0"
            elif relop == ">=":
                temp_var = self.variable_generator.get_new_int_variable()
                generated_code += (
                    f"ILSS {temp_var} {expression0_value} {expression1_value}\n"
                )
                generated_code += f"IEQL {relop_result_var} {temp_var} 0"
            else:
                print(
                    f"Error: Unsupported relational operator for integers: {relop}.",
                    file=sys.stderr,
                )
                raise Exception(
                    f"Unsupported relational operator for integers: {relop}"
                )

        return generated_code, relop_result_var

    def generate_expression(self, p):

        generated_code = f"{p.expression0.code}\n{p.term.code}\n"
        result_var = self.generate_temp_var()

        expression_type = self.get_expression_type(p.expression0.value)
        term_type = self.get_expression_type(p.term.value)

        if expression_type == FLOAT and term_type == INT:
            temp_var = self.variable_generator.get_new_float_variable()
            generated_code += (
                self.generate_conversion(INT, p.term.value, temp_var) + "\n"
            )
            term_value = temp_var
            term_type = FLOAT
            result_type = FLOAT
        elif expression_type == INT and term_type == FLOAT:
            temp_var = self.variable_generator.get_new_float_variable()
            generated_code += (
                self.generate_conversion(INT, p.expression.value, temp_var) + "\n"
            )
            expression_value = temp_var
            expression_type = FLOAT
            result_type = FLOAT
        elif expression_type == FLOAT and term_type == FLOAT:
            result_type = FLOAT
        else:
            result_type = INT

        if result_type == FLOAT:
            if p.ADDOP == PLUS:
                generated_code += (
                    f"{RADD} {result_var} {p.expression.value} {p.term.value}"
                )
            elif p.ADDOP == MINUS:
                generated_code += (
                    f"{RSUB} {result_var} {p.expression.value} {p.term.value}"
                )
            else:
                print(
                    f"Error: Unsupported operator for floats: {p.ADDOP}.",
                    file=sys.stderr,
                )
                raise Exception(f"Unsupported operator for floats: {p.ADDOP}")
        else:
            if p.ADDOP == PLUS:
                generated_code += (
                    f"{IADD} {result_var} {p.expression.value} {p.term.value}"
                )
            elif p.ADDOP == MINUS:
                generated_code += (
                    f"{ISUB} {result_var} {p.expression.value} {p.term.value}"
                )
            else:
                print(
                    f"Error: Unsupported operator for integers: {p.ADDOP}.",
                    file=sys.stderr,
                )
                raise Exception(f"Unsupported operator for integers: {p.ADDOP}")

        return generated_code, result_var

    def generate_term(self, p):
        generated_code = f"{term_code}\n{factor_code}\n"
        result_var = self.generate_temp_var()

        term_type = self.get_expression_type(p.term.value)
        factor_type = self.get_expression_type(p.factor.value)

        if term_type == FLOAT and factor_type == INT:
            temp_var = self.generate_temp_var()
            generated_code += (
                self.generate_conversion(INT, p.factor.value, temp_var) + "\n"
            )
            factor_value = temp_var
            factor_type = FLOAT
            result_type = FLOAT
        elif term_type == INT and factor_type == FLOAT:
            temp_var = self.generate_temp_var()
            generated_code += (
                self.generate_conversion(INT, p.term.value, temp_var) + "\n"
            )
            term_value = temp_var
            term_type = FLOAT
            result_type = FLOAT
        elif term_type == FLOAT and factor_type == FLOAT:
            result_type = FLOAT
        else:
            result_type = INT

        if result_type == FLOAT:
            if p.MULOP == MULTIPLY:
                generated_code += f"{RMLT} {result_var} {p.term.value} {p.factor.value}"
            elif p.MULOP == DIVIDE:
                generated_code += f"{RDIV} {result_var} {p.term.value} {p.factor.value}"
            else:
                print(
                    f"Error: Unsupported operator for floats: {p.MULOP}.",
                    file=sys.stderr,
                )
                raise Exception(f"Unsupported operator for floats: {p.MULOP}")
        else:
            if p.MULOP == MULTIPLY:
                generated_code += f"{IMLT} {result_var} {p.term.value} {p.factor.value}"
            elif p.MULOP == DIVIDE:
                generated_code += f"{IDIV} {result_var} {p.term.value} {p.factor.value}"
            else:
                print(
                    f"Error: Unsupported operator for integers: {p.MULOP}.",
                    file=sys.stderr,
                )
                raise Exception(f"Unsupported operator for integers: {p.MULOP}")

        return generated_code, result_var

    def generate_cast(self, p):
        cast_result_var = self.generate_temp_var()
        generated_code = f"{p.expression.code}\n"
        expression_type = self.get_expression_type(p.expression.value)
        if expression_type == p.cast:
            return generated_code, p.expression.value
        elif expression_type == INT and p.cast == FLOAT:
            generated_code += self.generate_conversion(
                INT, p.expression.value, cast_result_var
            )
            return generated_code, cast_result_var
        elif expression_type == FLOAT and p.cast == INT:
            generated_code += self.generate_conversion(
                FLOAT, p.expression.value, cast_result_var
            )
            return generated_code, cast_result_var
        else:
            print(f"Error: Cannot cast {expression_type} to {p.cast}.", file=sys.stderr)
            raise Exception(f"Cannot cast {expression_type} to {p.cast}")
