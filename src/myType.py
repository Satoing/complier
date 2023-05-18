from enum import Enum

class TokenType(Enum):
    BEGIN = 1
    END = 2
    INTEGER = 3
    IF = 4
    THEN = 5
    ELSE = 6
    FUNCTION = 7
    READ = 8
    WRITE = 9
    IDENTIFIER = 10
    CONSTANT = 11
    EQUAL = 12
    NOT_EQUAL = 13
    LESS_THAN_OR_EQUAL = 14
    LESS_THAN = 15
    GREATER_THAN_OR_EQUAL = 16
    GREATER_THAN = 17
    SUBTRACT = 18
    MULTIPLY = 19
    ASSIGN = 20
    LEFT_PARENTHESES = 21
    RIGHT_PARENTHESES = 22
    SEMICOLON = 23
    END_OF_LINE = 24
    END_OF_FILE = 25
    ERROR = 26

class Token(object):
    def __init__(self, mytype: TokenType, value: str):
        self.mytype = mytype
        self.value = value

    def __repr__(self):
        return f'[mytype: {self.mytype}, value: {self.value}]'

class Variable():
    def __init__(self, name, procedure, kind, mytype, level, address, line = -1, defined = False):
        self.name = name
        self.procedure = procedure
        self.kind = kind
        self.type = mytype
        self.level = level
        self.address = address
        self.defined = defined
        self.line = line
        
    def __repr__(self) -> str:
        return '{'+f'name: {self.name}, procedure: {self.procedure}, kind: {self.kind}, type: {self.type}, level: {self.level}, address: {self.address}'+'}'

class Procedure():
    def __init__(self, name, mytype, level, first, last):
        self.name = name
        self.type = mytype
        self.level = level
        self.first = first
        self.last = last
        
    def __repr__(self) -> str:
        return '{'+f'name: {self.name}, type: {self.type}, level: {self.level}, first: {self.first}, last: {self.last}'+'}'

if __name__ == "__main__":
    t = Token(TokenType.BEGIN, '+')
    print(t.mytype.value[0])