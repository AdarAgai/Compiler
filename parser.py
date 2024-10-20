from sly import Parser
from lexer import CPLLexer
from symbol_table import SymbolTable
from quad_generator import QuadGenerator
import sys
from quad_result import QuadResult 
from consts import INT, FLOAT

class CPLParser(Parser):

    # If there are errors, we will return an empty QuadResult object so we can continue to search for more errors

    tokens = CPLLexer.tokens

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors_found = False
        self.quad_generator = QuadGenerator(symbol_table=self.symbol_table)

    @_('declarations stmt_block')
    def program(self, p):
        return QuadResult(p.declarations.code + p.stmt_block.code)

    @_('declarations declaration')
    def declarations(self, p):
        return QuadResult(p.declarations.code + p.declaration.code)

    @_('')
    def declarations(self, p):
        return QuadResult("")

    @_('idlist ":" type ";"')
    def declaration(self, p):
        for var in p.idlist:
            if self.symbol_table.contains(var):
                print(f"Error: Variable '{var}' redeclared on line {p.lineno}.", file=sys.stderr)
                self.errors_found = True
            self.symbol_table.add(var, p.type)
        return QuadResult("") 

    @_('INT')
    def type(self, p):
        return INT

    @_('FLOAT')
    def type(self, p):
        return FLOAT

    @_('idlist "," ID')
    def idlist(self, p):
        return p.idlist + [p.ID] # return a list of IDs so we can iterate over them

    @_('ID')
    def idlist(self, p):
        return [p.ID] # return a list of the ID so it can iterable

    @_('assignment_stmt', 'input_stmt', 'output_stmt', 'if_stmt', 'while_stmt', 'stmt_block')   
    def stmt(self, p):
        return QuadResult(p[0].code)

    @_('ID "=" expression ";"')
    def assignment_stmt(self, p):
        if not self.symbol_table.contains(p.ID):
            print(f"Error: Variable '{p.ID}' not declared.", file=sys.stderr)
            self.errors_found = True
        try:
            return self.quad_generator.generate_assignment(p)
        except Exception:
            self.errors_found = True
            return QuadResult("")

    @_('INPUT "(" ID ")" ";"')
    def input_stmt(self, p):
        if not self.symbol_table.contains(p.ID):
            print(f"Error: Variable '{p.ID}' not declared.", file=sys.stderr)
            self.errors_found = True
        return self.quad_generator.generate_input(p)

    @_('OUTPUT "(" expression ")" ";"')
    def output_stmt(self, p):
        if p.expression.value is None:
            self.errors_found = True
            return QuadResult("")
        return self.quad_generator.generate_output(p)

    @_('IF "(" boolexpr ")" stmt ELSE stmt')
    def if_stmt(self, p):
        if p.boolexpr.value is None:
            self.errors_found = True
            return QuadResult("")
        return self.quad_generator.generate_if(p, p.stmt0.code, p.stmt1.code) 

    @_('WHILE "(" boolexpr ")" stmt')      
    def while_stmt(self, p):
        if p.boolexpr.value is None:
            self.errors_found = True
            return QuadResult("")
        return self.quad_generator.generate_while(p)

    @_('"{" stmtlist "}"')
    def stmt_block(self, p):
        return QuadResult(p.stmtlist.code)

    @_('stmt stmtlist')
    def stmtlist(self, p):
        return QuadResult(p.stmt.code + "\n" + p.stmtlist.code)

    @_('')
    def stmtlist(self, p):
        return QuadResult("")

    @_('boolexpr OR boolterm')
    def boolexpr(self, p):
        if p.boolexpr.value is None or p.boolterm.value is None:
            self.errors_found = True
            return QuadResult("")
        return self.quad_generator.generate_or(p)

    @_('boolterm')
    def boolexpr(self, p):
        if p.boolterm.value is None:
            self.errors_found = True
            return QuadResult("")
        return p.boolterm

    @_('boolterm AND boolfactor')
    def boolterm(self, p):
        if p.boolterm.value is None or p.boolfactor.value is None:
            self.errors_found = True
            return QuadResult("")
        return self.quad_generator.generate_and(p)

    @_('boolfactor')
    def boolterm(self, p):
        if p.boolfactor.value is None:
            self.errors_found = True
            return QuadResult("")
        return p.boolfactor

    @_('NOT "(" boolexpr ")"')
    def boolfactor(self, p):
        if p.boolexpr.value is None:
            self.errors_found = True
            return QuadResult("")
        return self.quad_generator.generate_not(p)

    @_('expression RELOP expression')
    def boolfactor(self, p):
        if p.expression0.value is None or p.expression1.value is None:
            self.errors_found = True
            return QuadResult("")
        result = self.quad_generator.generate_relop(p) 
        return result   

    @_('expression ADDOP term')
    def expression(self, p):
        if p.expression.value is None or p.term.value is None:
            self.errors_found = True
            return QuadResult("")
        try:
            return self.quad_generator.generate_expression(p)
        except Exception as e:
            print(e)
            self.errors_found = True
            return QuadResult("")

    @_('term')
    def expression(self, p):
        if p.term.value is None:
            self.errors_found = True
            return QuadResult("")
        return p.term

    @_('term MULOP factor')
    def term(self, p):
        if p.term.value is None or p.factor.value is None:
            self.errors_found = True
            return QuadResult("")
        try:
            return self.quad_generator.generate_term(p)
        except Exception as e:
            print(e)
            self.errors_found = True
            return QuadResult("")

    @_('factor')
    def term(self, p):
        if p.factor.value is None:
            self.errors_found = True
            return QuadResult("")
        return p.factor

    @_('"(" expression ")"')
    def factor(self, p):
        if p.expression.value is None:
            self.errors_found = True
            return QuadResult("")
        return p.expression

    @_('CAST "(" expression ")"')  
    def factor(self, p):
        if p.expression.value is None:
            self.errors_found = True
            return QuadResult("")
        try:
            return self.quad_generator.generate_cast(p)  
        except Exception:
            self.errors_found = True
            return QuadResult("")

    @_('ID')
    def factor(self, p):
        if not self.symbol_table.contains(p.ID):
            print(f"Error: Variable '{p.ID}' not declared.", file=sys.stderr)
            self.errors_found = True
        return QuadResult("", p.ID)

    @_('NUM')
    def factor(self, p):
        return QuadResult("", p.NUM)

    def error(self, p):
        if not p:
            print("Syntax error: EOF", file=sys.stderr) # useful for a program that has no {} for example
        else:
            print(f"Syntax error at line {p.lineno}.", file=sys.stderr)

        self.errors_found = True
        
        self.restart() # restart the parser so we can continue to search for more errors
        