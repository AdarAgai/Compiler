from utils import *
import sys
from quad_result import QuadResult

class QuadGenerator:

    def __init__(self, symbol_table):
        self.temp_int_count = 0
        self.temp_float_count = 0
        self.temp_label_count = 0
        self.symbol_table = symbol_table

    def generate_conversion(self, source_type, source_value, temp_var):
        if source_type == INT:
            return f"{ITOR} {temp_var} {source_value}"
        else:
            return f"{RTOI} {temp_var} {source_value}"

    def get_type(self, expression_value):
        if expression_value.isdigit() or self.symbol_table.get(expression_value) == INT or expression_value.startswith("int_temp"):
            return INT
        elif expression_value.replace(".", "", 1).isdigit() or self.symbol_table.get(expression_value) == FLOAT or expression_value.startswith("float_temp"):
            return FLOAT
        else:
            print(f"Error: Unknown expression type for {expression_value}", file=sys.stderr)
            raise Exception(f"Unknown expression type for {expression_value}")

    def generate_int_temp(self):
        self.temp_int_count += 1
        return f"int_temp_{self.temp_int_count}"

    def generate_float_temp(self):
        self.temp_float_count += 1
        return f"float_temp_{self.temp_float_count}"

    def generate_temp_label(self):
        self.temp_label_count += 1
        return f"label_temp_{self.temp_label_count}"

    def generate_assignment(self, p):

        variable_type = self.symbol_table.get(p.ID)
        expression_type = self.get_type(p.expression.value)
        generated_code = f"{p.expression.code}\n"

        if variable_type == INT and expression_type == INT:
            generated_code += f"{IASN} {p.ID} {p.expression.value}"
            return QuadResult(generated_code)

        elif variable_type == FLOAT and expression_type == FLOAT:
            generated_code += f"{RASN} {p.ID} {p.expression.value}"
            return QuadResult(generated_code)

        elif variable_type == FLOAT and expression_type == INT:
            temp_var = self.generate_int_temp()
            conversion_code = self.generate_conversion(INT, p.expression.value, temp_var)
            assignment_code = f"{RASN} {p.ID} {temp_var}\n"
            generated_code += f"{conversion_code}\n{assignment_code}"
            return QuadResult(generated_code)
        else:
            print(f"Error: Type mismatch on line {p.lineno}.", file=sys.stderr)
            raise Exception("Type mismatch")

    def generate_input(self, p):
        if self.symbol_table.get(p.ID) == INT:
            return QuadResult(f"{IINP} {p.ID}")
        else:
            return QuadResult(f"{RINP} {p.ID}")

    def generate_output(self, p):
        generated_code = f"{p.expression.code}\n"
        if self.get_type(p.expression.value) == INT:
            return QuadResult(generated_code + f"{IPRT} {p.expression.value}")
        else:
            return QuadResult(generated_code + f"{RPRT} {p.expression.value}")

    def generate_if(self, p, if_code, else_code):
        else_label = self.generate_temp_label()
        end_label = self.generate_temp_label()
        code = ""
        code += f"{p.boolexpr.code}\n"
        code += f"{JMPZ} {else_label} {p.boolexpr.value}\n"
        code += f"{if_code}\n"
        code += f"{JUMP} {end_label}\n"
        code += f"{else_label}: {else_code}\n"
        code += f"{end_label}:\n"
        return QuadResult(code)

    def generate_while(self, p):
        start_label = self.generate_temp_label()
        end_label = self.generate_temp_label()
        code = ""
        code += f"{start_label}:\n"
        code += f"{p.boolexpr.code}\n"
        code += f"{JMPZ} {end_label} {p.boolexpr.value}\n"
        code += f"{p.stmt.code}\n"
        code += f"{JUMP} {start_label}\n"
        code += f"{end_label}:\n"
        return QuadResult(code)

    def generate_or(self, p):
        end_label = self.generate_temp_label()
        false_label = self.generate_temp_label()
        or_result_var = self.generate_int_temp()

        code = ""
        code += f"{p.boolexpr.code}"
        code += f"{JMPZ} {false_label} {p.boolexpr.value}\n"
        code += f"{IASN} {or_result_var} 1\n"
        code += f"{JUMP} {end_label}\n"
        code += f"{false_label}: {p.boolterm.code}\n"
        code += f"{JMPZ} {false_label} {p.boolterm.value}\n"
        code += f"{IASN} {or_result_var} 1\n"
        code += f"{end_label}:\n"

        return QuadResult(code, or_result_var)

    def generate_and(self, p):
        end_label = self.generate_temp_label()
        false_label = self.generate_temp_label()
        and_result_var = self.generate_int_temp()

        code = ""
        code += f"{p.boolterm.code}"
        code += f"{JMPZ} {false_label} {p.boolterm.value}\n"
        code += f"{p.boolfactor.code}\n"
        code += f"{JMPZ} {false_label} {p.boolfactor.value}\n"
        code += f"{IASN} {and_result_var} 1\n"
        code += f"{JUMP} {end_label}\n"
        code += f"{false_label}: {IASN} {and_result_var} 0\n"
        code += f"{end_label}:\n"

        return QuadResult(code, and_result_var)

    def generate_not(self, p):
        not_result_var = self.generate_int_temp()

        code = ""
        code += f"{p.boolexpr.code}\n"
        code += f"{IEQL} {not_result_var} {p.boolexpr.value} 0\n"

        return QuadResult(code, not_result_var)

    def generate_relop(self, p):

        expression0_type = self.get_type(p.expression0.value)
        expression1_type = self.get_type(p.expression1.value)

        generated_code = f"{p.expression0.code}\n{p.expression1.code}\n"

        relop_result_var = ""

        expression0_value = p.expression0.value
        expression1_value = p.expression1.value

        if expression1_type == FLOAT and expression0_type == INT:
            temp_var = self.generate_float_temp()
            generated_code += self.generate_conversion(INT, p.expression0.value, temp_var) + "\n"
            expression0_value = temp_var
            expression0_type = FLOAT  
        elif expression1_type == INT and expression0_type == FLOAT:
            temp_var = self.generate_float_temp()
            generated_code += self.generate_conversion(INT, p.expression1.value, temp_var) + "\n"
            expression1_value = temp_var
            expression1_type = FLOAT  

        if expression0_type == FLOAT and expression1_type == FLOAT:
            relop_result_var = self.generate_float_temp()

            if p.RELOP == EQUAL:
                generated_code += f"REQL {relop_result_var} {expression0_value} {expression1_value}\n"
            elif p.RELOP == NOT_EQUAL:
                generated_code += f"RNQL {relop_result_var} {expression0_value} {expression1_value}\n"
            elif p.RELOP == LESS_THAN:
                generated_code += (
                    f"RLSS {relop_result_var} {expression0_value} {expression1_value}\n"
                )
            elif p.RELOP == GREATER_THAN:
                generated_code += (
                    f"RGRT {relop_result_var} {expression0_value} {expression1_value}\n"
                )
            elif p.RELOP == LESS_THAN_EQUAL:
                temp_var = self.generate_float_temp()
                generated_code += f"RGRT {relop_result_var} {expression0_value} {expression1_value}\n"
                generated_code += f"REQL {relop_result_var} {temp_var} 0\n"
            elif p.RELOP == GREATER_THAN_EQUAL:
                temp_var = self.generate_float_temp()
                generated_code += f"RLSS {relop_result_var} {expression0_value} {expression1_value}\n"
                generated_code += f"REQL {relop_result_var} {temp_var} 0\n"
            else:
                print(f"Error: Unsupported relational operator for floats: {p.RELOP}.", file=sys.stderr)
                raise Exception(
                    f"Unsupported relational operator for floats: {p.RELOP}"
                )

        elif expression0_type == INT and expression1_type == INT:
            relop_result_var = self.generate_int_temp()
            if p.RELOP == "==":
                generated_code += f"IEQL {relop_result_var} {expression0_value} {expression1_value}"
            elif p.RELOP == "!=":
                generated_code += f"INQL {relop_result_var} {expression0_value} {expression1_value}"
            elif p.RELOP == "<":
                generated_code += f"ILSS {relop_result_var} {expression0_value} {expression1_value}"
            elif p.RELOP == ">":
                generated_code += f"IGRT {relop_result_var} {expression0_value} {expression1_value}"
            elif p.RELOP == "<=":
                temp_var = self.generate_int_temp()
                generated_code += f"IGRT {temp_var} {expression0_value} {expression1_value}\n"
                generated_code += f"IEQL {relop_result_var} {temp_var} 0"
            elif p.RELOP == ">=":
                temp_var = self.generate_int_temp()
                generated_code += f"ILSS {temp_var} {expression0_value} {expression1_value}\n"
                generated_code += f"IEQL {relop_result_var} {temp_var} 0"
            else:
                print(
                    f"Error: Unsupported relational operator for integers: {p.RELOP}.",
                    file=sys.stderr,
                )
                raise Exception(
                    f"Unsupported relational operator for integers: {p.RELOP}"
                )

        return QuadResult(generated_code, relop_result_var)

    def generate_expression(self, p):
        generated_code = f"{p.expression.code}\n{p.term.code}\n"
        result_var = ""

        expression_type = self.get_type(p.expression.value)

        term_type = self.get_type(p.term.value)
        result_var = ""

        first_operand = p.expression.value
        second_operand = p.term.value

        if expression_type == FLOAT and term_type == INT:
            first_operand = self.generate_float_temp()
            generated_code += self.generate_conversion(INT, p.term.value, first_operand) + "\n"
            second_operand = p.expression.value
            term_type = FLOAT  
            result_type = FLOAT
        elif expression_type == INT and term_type == FLOAT:
            first_operand = self.generate_float_temp()
            generated_code += self.generate_conversion(INT, p.expression.value, first_operand) + "\n"
            second_operand = p.term.value
            expression_type = FLOAT
            result_type = FLOAT
        elif expression_type == FLOAT and term_type == FLOAT:
            result_type = FLOAT
        else:
            result_type = INT

        if result_type == FLOAT:

            result_var = self.generate_float_temp()
            if p.ADDOP == PLUS:
                generated_code += f"{RADD} {result_var} {first_operand} {second_operand}"
            elif p.ADDOP == MINUS:
                generated_code += (
                    f"{RSUB} {result_var} {first_operand} {second_operand}"
                )
            else:
                print(f"Error: Unsupported operator for floats: {p.ADDOP}.", file=sys.stderr)
                raise Exception(f"Unsupported operator for floats: {p.ADDOP}")
        else:

            result_var = self.generate_int_temp()
            if p.ADDOP == PLUS:
                generated_code += (
                    f"{IADD} {result_var} {first_operand} {second_operand}"
                )
            elif p.ADDOP == MINUS:
                generated_code += (
                    f"{ISUB} {result_var} {first_operand} {second_operand}"
                )
            else:
                print(f"Error: Unsupported operator for integers: {p.ADDOP}.", file=sys.stderr)
                raise Exception(f"Unsupported operator for integers: {p.ADDOP}")

        return QuadResult(generated_code, result_var)

    def generate_term(self, p):

        generated_code = f"{p.term.code}\n{p.factor.code}\n"
        result_var = ""

        term_type = self.get_type(p.term.value)
        factor_type = self.get_type(p.factor.value)

        first_operand = p.term.value
        second_operand = p.factor.value

        if term_type == FLOAT and factor_type == INT:
            first_operand = self.generate_float_temp()
            generated_code += (
                self.generate_conversion(INT, p.factor.value, first_operand) + "\n"
            )
            second_operand = p.term.value
            factor_type = FLOAT  
            result_type = FLOAT 
        elif term_type == INT and factor_type == FLOAT:
            first_operand = self.generate_float_temp()
            generated_code += (
                self.generate_conversion(INT, p.term.value, first_operand) + "\n"
            )
            second_operand = p.factor.value
            term_type = FLOAT
            result_type = FLOAT
        elif term_type == FLOAT and factor_type == FLOAT:

            result_type = FLOAT
        else:
            result_type = INT

        if result_type == FLOAT:
            result_var = self.generate_float_temp()
            if p.MULOP == MULTIPLY:
                generated_code += (
                    f"{RMLT} {result_var} {first_operand} {second_operand}"
                )
            elif p.MULOP == DIVIDE:
                generated_code += (
                    f"{RDIV} {result_var} {first_operand} {second_operand}"
                )
            else:
                print(f"Error: Unsupported operator for floats: {p.MULOP}.", file=sys.stderr)
                raise Exception(f"Unsupported operator for floats: {p.MULOP}")
        else:
            result_var = self.generate_int_temp()
            if p.MULOP == MULTIPLY:
                generated_code += (
                    f"{IMLT} {result_var} {first_operand} {second_operand}"
                )
            elif p.MULOP == DIVIDE:
                generated_code += (
                    f"{IDIV} {result_var} {first_operand} {second_operand}"
                )
            else:
                print(f"Error: Unsupported operator for integers: {p.MULOP}.", file=sys.stderr)
                raise Exception(f"Unsupported operator for integers: {p.MULOP}")
        return QuadResult(generated_code, result_var)

    def generate_cast(self, p):
        generated_code = f"{p.expression.code}\n"
        expression_type = self.get_type(p.expression.value)
        target_type = self.extract_cast_type(p.CAST)
        if expression_type == target_type:
            return QuadResult(generated_code, p.expression.value)
        elif expression_type == INT and target_type == FLOAT:
            cast_result_var = self.generate_float_temp()
            generated_code += self.generate_conversion(INT, p.expression.value, cast_result_var)
            return QuadResult(generated_code, cast_result_var)
        elif expression_type == FLOAT and target_type == INT:
            cast_result_var = self.generate_int_temp()
            generated_code += self.generate_conversion(FLOAT, p.expression.value, cast_result_var)
            return QuadResult(generated_code, cast_result_var)
        else:
            print(
                f"Error: Cannot cast {expression_type} to w{target_type}.",
                file=sys.stderr,
            )
            raise Exception(f"Cannot cast {expression_type} to {target_type}")

    def extract_cast_type(self, cast_str):
        if "int" in cast_str:
            return INT
        elif "float" in cast_str:
            return FLOAT
        else:
            raise Exception(f"Unsupported cast type in {cast_str}")