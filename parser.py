from sly import Parser
from lexer import CPLLexer
from symbol_table import SymbolTable
from quad_generator import QuadGenerator
import sys


class CPLParser(Parser):

    tokens = CPLLexer.tokens

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors_found = False
        self.quad_generator = QuadGenerator(symbol_table=self.symbol_table)

    @_("declarations stmt_block")
    def program(self, p):
        print(p.declarations + p.stmt_block)
        return p.declarations + p.stmt_block

    @_("declarations declaration")
    def declarations(self, p):
        return p.declarations + p.declaration

    @_("")
    def declarations(self, p):
        return ""

    @_('idlist ":" type ";"')
    def declaration(self, p):
        for var in p.idlist:
            if self.symbol_table.contains(var):
                print(
                    f"Error: Variable '{var}' redeclared on line {p.lineno}.",
                    file=sys.stderr,
                )
                self.errors_found = True
            self.symbol_table.add(var, p.type)
        return ""  # not sure

    @_("INT")
    def type(self, p):
        return "int"

    @_("FLOAT")
    def type(self, p):
        return "float"

    @_('idlist "," ID')
    def idlist(self, p):
        if p.ID in p.idlist or self.symbol_table.contains(p.ID):
            print(
                f"Error: Variable '{p.ID}' redeclared on line {p.lineno}.",
                file=sys.stderr,
            )
            self.errors_found = True
        return p.idlist + [p.ID]

    @_("ID")
    def idlist(self, p):
        if self.symbol_table.contains(p.ID):
            print(
                f"Error: Variable '{p.ID}' redeclared on line {p.lineno}.",
                file=sys.stderr,
            )
            self.errors_found = True
        return [p.ID]

    @_(
        "assignment_stmt",
        "input_stmt",
        "output_stmt",
        "if_stmt",
        "while_stmt",
        "stmt_block",
    )
    def stmt(self, p):
        return p[0]

    @_('ID "=" expression ";"')
    def assignment_stmt(self, p):
        if not self.symbol_table.contains(p.ID):
            print(f"Error: Variable '{p.ID}' not declared.", file=sys.stderr)
            self.errors_found = True
        try:
            return self.quad_generator.generate_assignment_stmt(p)
        except Exception:
            self.errors_found = True
            return ""

    @_('INPUT "(" ID ")" ";"')
    def input_stmt(self, p):
        if not self.symbol_table.contains(p.ID):
            print(f"Error: Variable '{variable_name}' not declared.", file=sys.stderr)
            self.errors_found = True

        return self.quad_generator.generate_input_stmt(p)

    @_('OUTPUT "(" expression ")" ";"')
    def output_stmt(self, p):
        if (
            p.expression.value is None
        ):  # do not need to print error here, it is already handled in expression
            self.errors_found = True
            return ""
        return self.quad_generator.generate_output_stmt(p)

    @_('IF "(" boolexpr ")" stmt ELSE stmt')
    def if_stmt(self, p):
        if p.boolexpr.value is None:
            self.errors_found = True
            return ""
        return self.quad_generator.generate_if_stmt(p, p.stmt0.code, p.stmt1.code)

    @_('WHILE "(" boolexpr ")" stmt')
    def while_stmt(self, p):
        if p.boolexpr.value is None:
            self.errors_found = True
            return ""
        return self.quad_generator.generate_while_stmt(p)

    @_('"{" stmtlist "}"')
    def stmt_block(self, p):
        return p.stmtlist.code

    @_("stmt stmtlist")
    def stmtlist(self, p):
        return p.stmt.code + "\n" + p.stmtlist.code

    @_("")
    def stmtlist(self, p):
        return ""

    @_("boolexpr OR boolterm")
    def boolexpr(self, p):
        if p.boolexpr.value is None or p.boolterm.value is None:
            self.errors_found = True
            return ""
        return self.quad_generator.generate_or(p)

    @_("boolterm")
    def boolexpr(self, p):
        if p.boolterm.value is None:
            self.errors_found = True
            return ""
        return p.boolterm

    @_("boolterm AND boolfactor")
    def boolterm(self, p):
        if p.boolterm.value is None or p.boolfactor.value is None:
            self.errors_found = True
            return ""
        return self.quad_generator.generate_and(p)

    @_("boolfactor")
    def boolterm(self, p):
        if p.boolfactor.value is None:
            self.errors_found = True
            return ""
        return p.boolfactor

    @_('NOT "(" boolexpr ")"')
    def boolfactor(self, p):
        if p.boolexpr.value is None:
            self.errors_found = True
            return ""
        return self.quad_generator.generate_not(p)

    @_("expression RELOP expression")
    def boolfactor(self, p):
        if p.expression0.value is None or p.expression1.value is None:
            self.errors_found = True
            return ""
        return self.quad_generator.generate_relop(p)

    @_("expression ADDOP term")
    def expression(self, p):
        if p.expression.value is None or p.term.value is None:
            self.errors_found = True
            return ""
        try:
            return self.quad_generator.generate_expression(p)
        except Exception:
            self.errors_found = True
            return ""

    @_("term")
    def expression(self, p):
        if p.term.value is None:
            self.errors_found = True
            return ""
        return p.term

    @_("term MULOP factor")
    def term(self, p):
        if p.term.value is None or p.factor.value is None:
            self.errors_found = True
            return ""
        try:
            return self.quad_generator.generate_term(p)
        except Exception:
            self.errors_found = True
            return ""

    @_("factor")
    def term(self, p):
        if p.factor.value is None:
            self.errors_found = True
            return ""
        return p.factor

    @_('"(" expression ")"')
    def factor(self, p):
        if p.expression.value is None:
            self.errors_found = True
            return ""
        return p.expression

    @_('CAST "(" expression ")"')
    def factor(self, p):
        if p.expression.value is None:
            self.errors_found = True
            return ""
        try:
            return self.quad_generator.generate_cast(p)
        except Exception:
            self.errors_found = True
            return ""

    @_("ID")
    def factor(self, p):
        if not self.symbol_table.contains(p.ID):
            print(f"Error: Variable '{p.ID}' not declared.", file=sys.stderr)
            self.errors_found = True
        return p.ID

    @_("NUM")
    def factor(self, p):
        return p.NUM
