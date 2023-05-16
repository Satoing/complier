import sys;sys.path.append("..")
from myType import TokenType, Token, Varible, Procedure
from cursor import Cursor
from config import *

class Parser():
    # 成员变量：文件内容
    def __init__(self):
        self.line = 1 # 统计第几行的错误
        self.callStack = ["main"] # 从main函数开始调用
        self.cursor = Cursor(Parser.readTokens()) # 将token作为输入
        self.currentVariableAddress = -1 # 当前还没有读取变量
        self.shouldAddError = True
        self.correctTokens = [] # 二元式
        self.variables = [] # 变量表
        self.procedures = [] # 过程表
        self.errors = [] # 错误信息文件
        
    def parse(self):
        pass
    
    def parseProgram(self):
        pass
    
    def parseSubprogram(self):
        pass
    
    def parseDeclarations(self):
        pass
    
    def parseDeclarations_(self):
        pass
    
    def parseDeclaration(self):
        pass
    
    def parseVariableDeclaration(self):
        pass
    
    def parseVariable(self):
        pass
    
    def parseProcedureDeclaration(self):
        pass
    
    def parseProcedureNameDeclaration(self):
        pass
    
    def parseProcedureName(self):
        pass
    
    def parseParameterDeclaration(self):
        pass
    
    def parseProcedureBody(self):
        pass
    
    def parseExecutions(self):
        pass
    
    def parseExecutions_(self):
        pass
    
    def parseExecution(self):
        pass
    
    def parseRead(self):
        pass
    
    def parseWrite(self):
        pass
    
    def parseAssignment(self):
        pass
    
    def parseArithmeticExpression(self):
        pass
    
    def parseArithmeticExpression_(self):
        pass
    
    def parseTerm(self):
        pass
    
    def parseTerm_(self):
        pass
    
    def parseFactor(self):
        pass
    
    def parseProcedureCall(self):
        pass
    
    def parseCondition(self):
        pass
    
    def parseConditionExpression(self):
        pass
    
    def parseOperator(self):
        pass
    
    def hasType(self, expectation: TokenType):
        return expectation == self.cursor.current.mytype
    
    def match(self, expectation, msg):
        if not self.hasType(expectation):
            if msg is None:
                msg = f'Expect {Parser.translateToken(expectation)}, but got {self.cursor.current().value}'
            self.addError(msg)
        return self.consumeToken()
    
    def consumeToken(self):
        self.goToNextLine()
        token = self.cursor.consume()
        self.correctTokens.append(token)
        self.goToNextLine()
        return token
    
    def goToNextLine(self):
        # 跳过多余的空行
        while self.cursor.isOpen() and self.hasType(TokenType.END_OF_LINE):
            token = self.cursor.consume()
            self.correctTokens.append(token)
            self.line += 1
            self.shouldAddError = True
            
    def addError(self, error: str):
        if not self.shouldAddError: return
        self.shouldAddError = False
        self.errors.append(f'Line{self.line}: {error}')
        
    @staticmethod
    def readTokens():
        f = open('../'+DYD_PATH)
        text = f.read().strip()
        tokens = []
        
        for line in text.split('\n'):
            value, mytype = line.strip().split(" ")
            if (not value) or (not value): continue
            tokens.append(Token(TokenType(int(mytype)), value))
        
        return tokens  
    
    @staticmethod
    def translateToken(mytype: TokenType):
        tokenTranslation = {
            TokenType.BEGIN: "'begin'",
            TokenType.END: "'end'",
            TokenType.INTEGER: "'integer'",
            TokenType.IF: "'if'",
            TokenType.THEN: "'then'",
            TokenType.ELSE: "'else'",
            TokenType.FUNCTION: "'function'",
            TokenType.READ: "'read'",
            TokenType.WRITE: "'write'",
            TokenType.IDENTIFIER: "identifier",
            TokenType.CONSTANT: "constant",
            TokenType.EQUAL: "'='",
            TokenType.NOT_EQUAL: "'<>'",
            TokenType.LESS_THAN_OR_EQUAL: "'<='",
            TokenType.LESS_THAN: "'<'",
            TokenType.GREATER_THAN_OR_EQUAL: "'>='",
            TokenType.GREATER_THAN: "'>'",
            TokenType.SUBTRACT: "'-'",
            TokenType.MULTIPLY: "'*'",
            TokenType.ASSIGN: "':='",
            TokenType.LEFT_PARENTHESES: "'('",
            TokenType.RIGHT_PARENTHESES: "')'",
            TokenType.SEMICOLON: "';'",
            TokenType.END_OF_LINE: "EOLN",
            TokenType.END_OF_FILE: "EOF",
        }
        return tokenTranslation[mytype];
    
if __name__ == "__main__":
    p = Parser()   
    print(p.translateToken(TokenType(1)))             