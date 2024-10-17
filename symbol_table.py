class SymbolTable():
    def __init__(self):
        self.symbol_table = {}
    def add(self, name, var_type):
        if name not in self.symbol_table:
            self.symbol_table[name] = var_type
    def get(self, name):
        try:
            return self.symbol_table[name]
        except KeyError:
            return None
    def contains(self, name):
        return name in self.symbol_table
    def __str__(self):
        return str(self.symbol_table)
    def __repr__(self):
        return str(self.symbol_table)