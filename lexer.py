from sly import Lexer
import sys

class CPLLexer(Lexer):
    tokens = {
        ELSE,
        FLOAT,
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
    NUM = r'\d+(\.\d*)?'
    INPUT = r'input'
    IF = r'if'
    RELOP = r'==|!=|<|>|>=|<='
    ADDOP = r'\+|-'
    MULOP = r'\*|/'
    OR = r'\|\|'
    AND = r'&&'
    NOT = r'!'
    CAST = r'static_cast<int>|static_cast<float>'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    def __init__(self):
        super().__init__()
        self.lineno = 1

    def error(self, t):
        print(f"Illegal character {t.value[0]} at line {self.lineno}", file=sys.stderr)
        self.index += 1  
