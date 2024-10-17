from sly import Lexer
import sys

class CPLLexer(Lexer):
    tokens = {
        ELSE,
        IF,
        INPUT,
        OUTPUT,
        WHILE,
        RELOP,
        ADDOP,
        MULOP,
        NUM,
        OR,
        AND,
        NOT,
        CAST,
        ID,
        INT,
        FLOAT
    }

    literals = { '=', ';', '(', ')', '{', '}', ',', ':' }

    ignore = ' \t'
    ignore_comment = r"/\*(.|\n)*?\*/"

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    INT = r'int'
    FLOAT = r'float'
    INPUT = r'input'
    OUTPUT = r'output'
    ELSE = r'else'
    IF = r'if'
    WHILE = r'while'
    RELOP = r"==|!=|>=|<=|<|>"
    CAST = r'static_cast<int>|static_cast<float>'
    ADDOP = r'\+|-'
    MULOP = r'\*|/'
    OR = r'\|\|'
    AND = r'&&'
    NOT = r'!'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NUM = r'\d+(\.\d*)?'

    def __init__(self):
        super().__init__()
        self.lineno = 1

    def error(self, t):
        print(f"Illegal character {t.value[0]} at line {self.lineno}", file=sys.stderr)
        self.index += 1  
