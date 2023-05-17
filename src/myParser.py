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
        self.correctTokens = [] # 二元式表
        self.variables = [] # 变量表
        self.procedures = [] # 过程表
        self.errors = [] # 错误信息文件
        
    def parse(self):
        try:
            self.parseProgram()
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(e + '[FATAL]')
            return False
        finally:
            # 写入文件
            pass
    
    def parseProgram(self):
        # <程序> -> <分程序>
        self.parseSubprogram()
        self.match(TokenType.END_OF_FILE)
    
    def parseSubprogram(self):
        # <分程序> -> begin <说明语句表>; <执行语句表> end
        self.match(TokenType.BEGIN)
        self.parseDeclarations()
        self.parseExecutions()
        self.match(TokenType.END)
    
    def parseDeclarations(self):
        # <说明语句表> -> <说明语句> | <说明语句表>; <说明语句>
        self.parseDeclaration()
        self.parseDeclarations_()
    
    def parseDeclarations_(self):
        # 需要判断是否是类型说明（这里就是INTEGER）
        if self.hasType(TokenType.INTEGER):
            self.parseDeclaration()
            self.parseDeclarations_()
    
    def parseDeclaration(self):
        # 消除公共左因子
        self.match(TokenType.INTEGER)
        self.parseDeclaration_()
        self.match(TokenType.SEMICOLON)

    def parseDeclaration_(self):
        # 区别变量声明和函数声明
        if self.hasType(TokenType.IDENTIFIER): # 变量声明
            self.parseVariableDeclaration()
            return
        elif self.hasType(TokenType.FUNCTION):
            self.parseProcedureDeclaration()
            return
        value = self.consumeToken()
        self.throwError(f'{value} is not a valid variable name')

    def parseVariableDeclaration(self):
        # 需要把变量写进变量表
        value = self.match(TokenType.IDENTIFIER)
        self.registerVariable(value)
    
    def parseVariable(self):
        self.match(TokenType.IDENTIFIER)
        if not self.findVariable(value):
            self.addError(f'Undefined variable {value}')
    
    def parseProcedureDeclaration(self):
        self.match(TokenType.FUNCTION)
        self.parseProcedureNameDeclaration()
        self.match(TokenType.LEFT_PARENTHESES)
        self.parseParameterDeclaration()
        # 右括号需要与左括号匹配
        self.match(TokenType.RIGHT_PARENTHESES, "Unmatched '('")
        self.match(TokenType.SEMICOLON)
        self.parseProcedureBody()
    
    def parseProcedureNameDeclaration(self):
        value = self.match(TokenType.IDENTIFIER)
        self.registerProcedure(value)
    
    def parseProcedureName(self):
        value = self.match(TokenType.IDENTIFIER)
        if not self.findProcedure(value):
            self.addError(f'Unidefined procedure {value}')
    
    def parseParameterDeclaration(self):
        value = self.match(TokenType.IDENTIFIER)
        self.registerParameter(value)
    
    def parseProcedureBody(self):
        self.match(TokenType.BEGIN)
        self.parseDeclarations()
        self.parseExecutions()
        self.match(TokenType.END)
        # 函过程调用栈的处理（删除第一个元素）
        self.callStack.pop(0)
    
    def parseExecutions(self):
        self.parseExecution()
        self.parseExecutions_()
    
    def parseExecutions_(self):
        if self.hasType(TokenType.SEMICOLON):
            self.match(TokenType.SEMICOLON)
            self.parseExecution()
            self.parseExecutions_()
    
    def parseExecution(self):
        # read语句
        if self.hasType(TokenType.READ):
            self.parseRead();
            return
        # write语句
        elif self.hasType(TokenType.WRITE):
            self.parseWrite()
            return
        # 赋值语句
        elif self.hasType(TokenType.IDENTIFIER):
            self.parseAssignment()
            return
        # 条件语句
        elif self.hasType(TokenType.IF):
            self.parseCondition()
            return 
        # 出错处理
        value = self.consumeToken()
        self.throwError(f'Expect executions, but got {value}. Please move all declarations to the beginning of the procedure')
    
    def parseRead(self):
        self.match(TokenType.READ)
        self.match(TokenType.LEFT_PARENTHESES)
        self.parseVariable()
        self.match(TokenType.RIGHT_PARENTHESES)
    
    def parseWrite(self):
        self.match(TokenType.WRITE)
        self.match(TokenType.LEFT_PARENTHESES)
        self.parseVariable()
        self.match(TokenType.RIGHT_PARENTHESES)
    
    def parseAssignment(self):
        if self.findVariable(self.cursor.current().value):
            self.parseVariable()
        elif self.findProcedure(self.cursor.current().value):
            self.parseProcedureName()
        else:
            value = self.consumeToken()
            self.addError(f'Unidefined variable or procedure {value}')

        self.match(TokenType.ASSIGN)
        self.parseArithmeticExpression()

    def parseArithmeticExpression(self):
        self.parseTerm()
        self.parseArithmeticExpression_()
    
    def parseArithmeticExpression_(self):
        if self.hasType(TokenType.SUBTRACT):
            self.match(TokenType.SUBTRACT)
            self.parseTerm()
            self.parseArithmeticExpression_()
    
    def parseTerm(self):
        self.parseFactor()
        self.parseTerm_()
    
    def parseTerm_(self):
        if self.hasType(TokenType.MULTIPLY):
            self.match(TokenType.MULTIPLY)
            self.parseFactor()
            self.parseTerm_()
    
    def parseFactor(self):
        if self.hasType(TokenType.CONSTANT):
            self.match(TokenType.CONSTANT)
            return
        elif self.hasType(TokenType.IDENTIFIER):
            if self.findVariable(self.cursor.current().value):
                self.parseVariable()
                return
            elif self.findProcedure(self.cursor.current().value):
                self.parseProcedureCall()
                return
            value = self.consumeToken()
            self.throwError(f'Undefined variable or procedure {value}')
        
        value = self.consumeToken()
        self.throwError(f'Expect variable, procedure or constant, but got {value}')
    
    def parseProcedureCall(self):
        self.parseProcedureName()
        self.match(TokenType.LEFT_PARENTHESES)
        self.parseArithmeticExpression()
        self.match(TokenType.RIGHT_PARENTHESES, "Unmatched '('")
    
    def parseCondition(self):
        self.match(TokenType.IF)
        self.parseConditionExpression()
        self.match(TokenType.THEN)
        self.parseExecution()
        self.match(TokenType.ELSE)
        self.parseExecution()
    
    def parseConditionExpression(self):
        self.parseArithmeticExpression()
        self.parseOperator()
        self.parseArithmeticExpression()
    
    def parseOperator(self):
        # 匹配各种关系运算符
        if self.hasType(TokenType.EQUAL):
            self.match(TokenType.EQUAL)
            return
        elif self.hasType(TokenType.NOT_EQUAL):
            self.match(TokenType.NOT_EQUAL)
            return
        elif self.hasType(TokenType.LESS_THAN):
            self.match(TokenType.LESS_THAN)
            return
        elif self.hasType(TokenType.LESS_THAN_OR_EQUAL):
            self.match(TokenType.LESS_THAN_OR_EQUAL)
            return
        elif self.hasType(TokenType.GREATER_THAN):
            self.match(TokenType.GREATER_THAN)
            return
        elif self.hasType(TokenType.GREATER_THAN_OR_EQUAL):
            self.match(TokenType.GREATER_THAN_OR_EQUAL)
            return
        
        value = self.consumeToken()
        self.addError(f'{value} is not a valid operator')
        
    def registerVariable(self, name: str):
        if self.findParameter(name): return
        
        duplicateVariable = self.findDuplicateVariable(name)
        
        if duplicateVariable:
            self.addError(f'Variable {name} has already been declared')
            return
        
        # 定义最外层变量的过程为_start
        procedure = "_start"
        if self.callStack[0] is not None:  procedure = self.callStack[0]
        self.variables.append(Varible(name, procedure, 0, "integer", len(self.callStack), self.currentVariableAddress))
        self.currentVariableAddress += 1
        
        self.updateProcedureVariableAddresses()
    
    def findDuplicateVariable(self, name: str):
        flag = False
        for var in self.variables:
            if var.name == name and var.procedure == self.callStack[0]:
                flag = True;break
        return flag
    
    def findVariable(self, name: str):
        flag = False
        for var in self.variables:
            if var.name == name and var.level <= len(self.callStack):
                flag = True;break
        return flag
    
    def registerParameter(self, name: str):        
        duplicateParameter = self.findDuplicateParameter(name)
        
        if duplicateParameter:
            self.addError(f'Parameter {name} has already been declared')
            return
        
        # 定义最外层变量的过程为_start
        procedure = "_start"
        if self.callStack[0] is not None:  procedure = self.callStack[0]
        self.variables.append(Varible(name, procedure, 1, "integer", len(self.callStack), self.currentVariableAddress))
        self.currentVariableAddress += 1
        
        self.updateProcedureVariableAddresses()
    
    def findDuplicateParameter(self, name: str):
        flag = False
        for var in self.variables:
            if var.name == name and var.kind == 1 and var.procedure == self.callStack[0]:
                flag = True;break
        return flag
    
    def findParameter(self, name: str):
        flag = False
        for var in self.variables:
            if var.name == name and var.kind == 1 and var.level <= len(self.callStack):
                flag = True;break
        return flag
    
    def registerProcedure(self, name: str):
        duplicateProcedure = self.findDuplicateProcedure(name)
        
        if duplicateProcedure:
            self.addError(f'Procedure {name} has already been declared')
            return
        
        self.procedures.append(Procedure(name, "integer", len(self.callStack)+1, -1, -1))
        
        self.callStack.insert(0, name)
    
    def findDuplicateProcedure(self, name: str):
        flag = False
        for pro in self.procedures:
            if pro.name == name and pro.level == len(self.callStack)+1:
                flag = True;break
        return flag
    
    def findProcedure(self, name: str):
        flag = False
        for pro in self.procedures:
            if pro.name == name and pro.level <= len(self.callStack)+1:
                flag = True;break
        return flag
    
    def updateProcedureVariableAddresses(self):
        pro = "_start"
        if self.callStack[0] is not None:  pro = self.callStack[0]
        procedure = self.findProcedure(pro)
        
        if not procedure: return
        
        if procedure.first == -1:
            procedure.first = self.currentVariableAddress
            
        procedure.last = self.currentVariableAddress
    
    def hasType(self, expectation: TokenType):
        return expectation == self.cursor.current.mytype
    
    def match(self, expectation: TokenType, msg = None):
        # 期望的与实际的符号不同，报错。如果传入了错误信息，则使用传入的
        if not self.hasType(expectation):
            if msg is None:
                msg = f'Expect {Parser.translateToken(expectation)}, but got {self.cursor.current().value}'
            self.addError(msg)
        # 即使符号与预期的不同也接收，只是增加报错信息。便于检查出尽可能多的错误
        return self.consumeToken()
    
    def consumeToken(self):
        # 加入前后都检查一下是否是行尾（感觉只需要在加入后检查）
        self.goToNextLine()
        token = self.cursor.consume()
        # 将正确的符号加入符号表
        self.correctTokens.append(token)
        self.goToNextLine()
        return token
    
    def goToNextLine(self):
        # 文件没结束且当前的符号是'\n'才移动到下一行，否则就什么也不做
        while self.cursor.isOpen() and self.hasType(TokenType.END_OF_LINE):
            token = self.cursor.consume() # 移到下一个符号
            self.correctTokens.append(token) # 将'\n'加入符号表
            self.line += 1 # 移动到下一行
            self.shouldAddError = True # 每一行只报一个错
            
    def addError(self, error: str):
        # 将错误信息添加到列表中，便于之后写入文件
        if not self.shouldAddError: return
        self.shouldAddError = False
        self.errors.append(f'Line{self.line}: {error}')

    def throwError(error: str):
        raise Exception(f'Line {self.line}: {error}')
        
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
        # 将TokenType与具体的符号联系起来，用于报错信息
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
    print(p.translateToken(TokenType.ASSIGN))