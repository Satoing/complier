import sys;sys.path.append("..")
from myType import TokenType, Token
from cursor import Cursor
from config import *

# 标志符的最大长度
MAX_IDENTIFIER_LENGTH = 16

class Lexer():
    # 成员变量：文件内容
    def __init__(self):
        self.line = 1 # 统计第几行的错误
        self.cursor = Cursor(Lexer.readSource())
        self.tokens = []
        self.errors = []
        self.tokenize()

    def tokenize(self):
        # 文件还没有读取完
        while self.cursor.isOpen():
            token = self.getNextToken()
            if token.mytype.name != 'ERROR':
                self.tokens.append(token)
            # 加入错误信息
            else: self.errors.append(token.value)
        
        # 放入文件结束符
        self.tokens.append(Token(TokenType.END_OF_FILE, 'EOF'))
        
        # 最后分别写入符号表和错误表
        self.writeTokens()
        self.writeErrors()
    
    def getNextToken(self):
        # 跳过空格
        while self.cursor.current() == ' ':
            self.cursor.consume() 
        
        # initial是符号的开始
        initial = self.cursor.consume()

        if Lexer.isLetter(initial): 
            value = initial
            # 读取整个标识符或关键字
            while self.cursor.isOpen() and (Lexer.isLetter(self.cursor.current()) or Lexer.isDigit(self.cursor.current())):
                value += self.cursor.consume()
            
            keywordType = Lexer.getKeywordType(value)
            if keywordType is not None:
                return Token(keywordType, value)
            # 标识符的情况
            elif len(value) <= MAX_IDENTIFIER_LENGTH:
                return Token(TokenType.IDENTIFIER, value)
            else:
                errmsg = f'Line{self.line}: Error3, Identifier name {value} exceeds {MAX_IDENTIFIER_LENGTH} characters'
                return Token(TokenType.ERROR, errmsg) 

        if Lexer.isDigit(initial): 
            value = initial
            while Lexer.isDigit(self.cursor.current()):
                value += self.cursor.consume()
            return Token(TokenType.CONSTANT, value)

        if initial == '=': return Token(TokenType.EQUAL, '=')

        if initial == '-': return Token(TokenType.SUBTRACT, '-')
        
        if initial == '*': return Token(TokenType.MULTIPLY, '*')

        if initial == '(': return Token(TokenType.LEFT_PARENTHESES, '(')

        if initial == ')': return Token(TokenType.RIGHT_PARENTHESES, ')')
        
        if initial == ';': return Token(TokenType.SEMICOLON, ';')

        if initial == '<': 
            if self.cursor.current() == '=':
                self.cursor.consume()
                return Token(TokenType.LESS_THAN_OR_EQUAL, '<=')
            elif self.cursor.current() == '>':
                self.cursor.consume()
                return Token(TokenType.NOT_EQUAL, '<>')
            return Token(TokenType.LESS_THAN, '<')

        if initial == '>': 
            if self.cursor.current() == '=':
                self.cursor.consume()
                return Token(TokenType.GREATER_THAN_OR_EQUAL, '>=')
            return Token(TokenType.GREATER_THAN, '>')

        if initial == ':':
            if self.cursor.current() == '=':
                self.cursor.consume()
                return Token(TokenType.ASSIGN, ':=')
            errmsg = f'Line{self.line}: Error2, Misused colon'
            return Token(TokenType.ERROR, errmsg)

        if initial == '\n': 
            self.line += 1
            return Token(TokenType.END_OF_LINE, 'EOLN')

        # 否则就是无法识别的字符返回
        errmsg = f'Line{self.line}: Error1, Invalid character {initial}'
        return Token(TokenType.ERROR, errmsg)
    
    def writeTokens(self):
        f = open("../"+DYD_PATH, mode='w')
        for token in self.tokens:
            f.write(f'{token.value.rjust(16)} {str(token.mytype.value[0]).rjust(2, "0")}\n')

    def writeErrors(self):
        f = open('../'+ERR_PATH, mode='w')
        for err in self.errors:
            f.write(err+'\n')

    @staticmethod
    def isLetter(value: str):
        return value.isalpha()
    
    @staticmethod
    def isDigit(value: str):
        return value.isdigit()
    
    # 判断是关键字还是标志符。如果是标识符就返回None
    @staticmethod
    def getKeywordType(value: str):
        v = value.lower()
        if v == 'begin': return TokenType.BEGIN
        elif v == 'end': return TokenType.END
        elif v == 'integer': return TokenType.INTEGER
        elif v == 'if': return TokenType.IF
        elif v == 'then': return TokenType.THEN
        elif v == 'else': return TokenType.ELSE
        elif v == 'function': return TokenType.FUNCTION
        elif v == 'read': return TokenType.READ
        elif v == 'write': return TokenType.WRITE
        return None

    @staticmethod
    def readSource():
        f = open("../"+SOURCE_PATH)
        return f.read()

if __name__ == "__main__":
    lex = Lexer()