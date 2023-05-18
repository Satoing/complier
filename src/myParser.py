import sys;sys.path.append("..")
if __name__ != "__main__":
    sys.path.append("src")
from myType import TokenType, Token, Variable, Procedure
from cursor import Cursor
from config import *

class Parser():
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
        self.parse()
        
    def parse(self):
        try:
            self.parseProgram()
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(str(e) + ' [FATAL]')
            return False
        finally:
            # 写入文件
            self.writeCorrectTokens()
            self.writeVariables()
            self.writeProcedures()
            self.writeErrors()
    
    def parseProgram(self):
        # <程序>→<分程序><EOF>
        self.parseSubprogram()
        self.match(TokenType.END_OF_FILE)
    
    def parseSubprogram(self):
        # <分程序>→begin <说明语句表><执行语句表> end
        self.match(TokenType.BEGIN)
        self.parseDeclarations()
        self.parseExecutions()
        self.match(TokenType.END)
    
    def parseDeclarations(self):
        # <说明语句表>→<说明语句><说明语句表'>
        self.parseDeclaration()
        self.parseDeclarations_()
    
    def parseDeclarations_(self):
        # <说明语句表'>→<说明语句><说明语句表'>|e
        if self.hasType(TokenType.INTEGER):
            self.parseDeclaration()
            self.parseDeclarations_()
    
    def parseDeclaration(self):
        # <说明语句>→integer <说明语句'>;
        self.match(TokenType.INTEGER)
        self.parseDeclaration_()
        self.match(TokenType.SEMICOLON)

    def parseDeclaration_(self):
        # <说明语句'>→<变量说明>│<函数说明>
        if self.hasType(TokenType.IDENTIFIER): # 变量声明
            self.parseVariableDeclaration()
            return
        elif self.hasType(TokenType.FUNCTION):
            self.parseProcedureDeclaration()
            return
        value = self.consumeToken().value
        self.throwError(f"'{value}' is not a valid variable name")

    def parseVariableDeclaration(self):
        # <变量说明>→<变量>
        value = self.match(TokenType.IDENTIFIER).value
        self.registerVariable(value)
    
    def parseVariable(self):
        # <变量>→<标识符>
        value = self.match(TokenType.IDENTIFIER).value
        if not self.findVariable(value):
            self.addError(f"Undefined variable '{value}'")
    
    def parseProcedureDeclaration(self):
        # <函数说明>→function <函数名>(<参数>);<函数体>
        self.match(TokenType.FUNCTION)
        self.parseProcedureNameDeclaration()
        self.match(TokenType.LEFT_PARENTHESES)
        self.parseParameterDeclaration()
        # 右括号需要与左括号匹配
        self.match(TokenType.RIGHT_PARENTHESES, "Unmatched '('")
        self.match(TokenType.SEMICOLON)
        self.parseProcedureBody()
    
    def parseProcedureNameDeclaration(self):
        # <函数名>→<标识符>
        value = self.match(TokenType.IDENTIFIER).value
        self.registerProcedure(value)
    
    def parseProcedureName(self):
        # # <函数名>→<标识符>
        value = self.match(TokenType.IDENTIFIER).value
        if not self.findProcedure(value):
            self.addError(f"Unidefined procedure '{value}'")
    
    def parseParameterDeclaration(self):
        # <形参>→<变量>
        value = self.match(TokenType.IDENTIFIER).value
        self.registerParameter(value)
    
    def parseProcedureBody(self):
        # <函数体>→begin <说明语句表><执行语句表> end
        self.match(TokenType.BEGIN)
        self.parseDeclarations()
        # 进入执行语句前检查函数的形参是否在说明语句表中定义
        self.checkParameterDeclared()
        self.parseExecutions()
        self.match(TokenType.END)
        # 函过程调用栈的处理
        self.callStack.pop()
    
    def parseExecutions(self):
        # <执行语句表>→<执行语句><执行语句表'>
        self.parseExecution()
        self.parseExecutions_()
    
    def parseExecutions_(self):
        # <执行语句表'>→;<执行语句><执行语句表'>|e
        if self.hasType(TokenType.SEMICOLON):
            self.match(TokenType.SEMICOLON)
            self.parseExecution()
            self.parseExecutions_()
    
    def parseExecution(self):
        # <执行语句>→<读语句>│<写语句>│<赋值语句>│<条件语句>
        if self.hasType(TokenType.READ):
            self.parseRead();
            return
        elif self.hasType(TokenType.WRITE):
            self.parseWrite()
            return
        elif self.hasType(TokenType.IDENTIFIER):
            self.parseAssignment()
            return
        elif self.hasType(TokenType.IF):
            self.parseCondition()
            return 
        # 出错处理
        value = self.consumeToken().value
        self.throwError(f"Expect executions, but got '{value}'. Please move all declarations to the beginning of the procedure")
    
    def parseRead(self):
        # <读语句>→read(<变量>)
        self.match(TokenType.READ)
        self.match(TokenType.LEFT_PARENTHESES)
        self.parseVariable()
        self.match(TokenType.RIGHT_PARENTHESES)
    
    def parseWrite(self):
        # <写语句>→write(<变量>)
        self.match(TokenType.WRITE)
        self.match(TokenType.LEFT_PARENTHESES)
        self.parseVariable()
        self.match(TokenType.RIGHT_PARENTHESES)
    
    def parseAssignment(self):
        # <赋值语句>→<变量>:=<算术表达式>|<函数名>:=<算术表达式>
        if self.findVariable(self.cursor.current().value):
            self.parseVariable()
        elif self.findProcedure(self.cursor.current().value):
            self.parseProcedureName()
        else:
            value = self.consumeToken().value
            self.addError(f"Unidefined variable or procedure '{value}'")

        self.match(TokenType.ASSIGN)
        self.parseArithmeticExpression()

    def parseArithmeticExpression(self):
        # <算术表达式>→<项><算术表达式'>
        self.parseTerm()
        self.parseArithmeticExpression_()
    
    def parseArithmeticExpression_(self):
        # <算术表达式'>→-<项><算术表达式'>|e
        if self.hasType(TokenType.SUBTRACT):
            self.match(TokenType.SUBTRACT)
            self.parseTerm()
            self.parseArithmeticExpression_()
    
    def parseTerm(self):
        # <项>→<因子><项'>
        self.parseFactor()
        self.parseTerm_()
    
    def parseTerm_(self):
        # <项'>→*<因子><项'>|e
        if self.hasType(TokenType.MULTIPLY):
            self.match(TokenType.MULTIPLY)
            self.parseFactor()
            self.parseTerm_()
    
    def parseFactor(self):
        # <因子>→<变量>│<常数>│<函数调用>
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
            value = self.consumeToken().value
            self.throwError(f"Undefined variable or procedure '{value}'")
        
        value = self.consumeToken().value
        self.throwError(f"Expect variable, procedure or constant, but got '{value}'")
    
    def parseProcedureCall(self):
        # <函数调用>→<函数名>(<算术表达式>)
        self.parseProcedureName()
        self.match(TokenType.LEFT_PARENTHESES)
        self.parseArithmeticExpression()
        self.match(TokenType.RIGHT_PARENTHESES, "Unmatched '('")
    
    def parseCondition(self):
        # <条件语句>→if<条件表达式>then<执行语句>else<执行语句>
        self.match(TokenType.IF)
        self.parseConditionExpression()
        self.match(TokenType.THEN)
        self.parseExecution()
        self.match(TokenType.ELSE)
        self.parseExecution()
    
    def parseConditionExpression(self):
        # <条件表达式>→<算术表达式><关系运算符><算术表达式>
        self.parseArithmeticExpression()
        self.parseOperator()
        self.parseArithmeticExpression()
    
    def parseOperator(self):
        # <关系运算符> →<│<=│>│>=│=│<>
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
        
        value = self.consumeToken().value
        self.addError(f"'{value}' is not a valid operator")
        
    def registerVariable(self, name: str):
        # 如果是形参，则已经加入过了，将defined属性改为True
        var = self.findParameter(name)
        if var: var.defined = True;return
        
        # 检查变量重定义的错误
        duplicateVariable = self.findDuplicateVariable(name)
        if duplicateVariable:
            self.addError(f"Variable '{name}' has already been declared")
            return
        
        # 需要加入的情况，将变量信息加入variables列表中，然后
        self.variables.append(Variable(name, self.callStack[-1], 0, "integer", len(self.callStack), self.currentVariableAddress+1))
        self.currentVariableAddress += 1
        # 动态更新相应过程的first和last
        self.updateProcedureVariableAddresses()
    
    def findDuplicateVariable(self, name: str):
        # 检查是否有在同一个过程中变量多次定义的情况
        for var in self.variables:
            if var.name == name and var.procedure == self.callStack[-1]:
                return var
    
    def findVariable(self, name: str):
        # 检查是否在该层定义过该变量，使用一个变量前都应该检查一下
        for var in self.variables:
            if var.name == name and var.level == len(self.callStack):
                return var
    
    def registerParameter(self, name: str):
        # 一开始直接按惯性思维认为函数可以传多个形参，之后再看文法才发现一个函数只能传一个参数
        # 但是也懒得改了，就这样吧
        duplicateParameter = self.findDuplicateParameter(name)
        if duplicateParameter:
            self.addError(f"Parameter '{name}' has already been declared")
            return
        
        self.variables.append(Variable(name, self.callStack[-1], 1, "integer", len(self.callStack), self.currentVariableAddress+1, self.line))
        self.currentVariableAddress += 1
        self.updateProcedureVariableAddresses()
    
    def findDuplicateParameter(self, name: str):
        for var in self.variables:
            if var.name == name and var.kind == 1 and var.procedure == self.callStack[-1]:
                return var
    
    def findParameter(self, name: str):
        # 检查当前变量是否是形参
        for var in self.variables:
            if var.name == name and var.kind == 1 and var.level <= len(self.callStack):
                return var
    
    def registerProcedure(self, name: str):
        # 检查是否存在同级过程重定义的情况。有就报错
        duplicateProcedure = self.findDuplicateProcedure(name)
        if duplicateProcedure:
            self.addError(f"Procedure '{name}' has already been declared")
            return
        # 在进行该操作的时候还没有处理形参，所以first和last都先初始化为-1。后面动态更新
        self.procedures.append(Procedure(name, "integer", len(self.callStack)+1, -1, -1))
        self.callStack.append(name)
    
    def findDuplicateProcedure(self, name: str):
        for pro in self.procedures:
            if pro.name == name and pro.level == len(self.callStack)+1:
                return pro
    
    def findProcedure(self, name: str):
        for pro in self.procedures:
            if pro.name == name and pro.level <= len(self.callStack)+1:
                return pro
    
    def updateProcedureVariableAddresses(self):
        procedure = self.findProcedure(self.callStack[-1])
        if not procedure: return
        
        # first只在第一次初始化
        if procedure.first == -1:
            procedure.first = self.currentVariableAddress
        # last需要不断更新
        procedure.last = self.currentVariableAddress
    
    def checkParameterDeclared(self):
        # 检查函数的形参是否定义。如果没定义就报错
        for var in self.variables:
            if var.level == len(self.callStack) and var.kind == 1 and var.defined == False:
                errmsg = f"Line {var.line}: parameter '{var.name}' is not declared in the function body"
                self.errors.append(errmsg)
            
    
    def hasType(self, expectation: TokenType):
        return expectation == self.cursor.current().mytype
    
    def match(self, expectation: TokenType, msg = None):
        # 期望的与实际的符号不同，报错。如果传入了错误信息，则使用传入的
        if not self.hasType(expectation):
            if msg is None:
                msg = f"Expect {Parser.translateToken(expectation)}, but got '{self.cursor.current().value}'"
            self.addError(msg)
        # 即使符号与预期的不同也接收，只是增加报错信息。便于检查出尽可能多的错误
        return self.consumeToken()
    
    def consumeToken(self):
        # self.goToNextLine()
        token = self.cursor.consume()
        # 将正确的符号加入符号表
        self.correctTokens.append(token)
        # 加入后检查一下是否是行尾
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
        self.errors.append(f'Line {self.line}: {error}')

    def throwError(self, error: str):
        raise Exception(f'Line {self.line}: {error}')
    
    def writeCorrectTokens(self):
        path = ''
        if __name__ == "__main__":
            path = '../'
        f = open(path+DYS_PATH, mode='w')
        for token in self.correctTokens:
            f.write(f'{token.value.rjust(16)} {str(token.mytype.value).rjust(2, "0")}\n')
    
    def writeVariables(self):
        path = ''
        if __name__ == "__main__": path = '../'
        f = open(path+VAR_PATH, mode='w')
        for var in self.variables:
            f.write(f'{var.name.rjust(16)} {var.procedure.rjust(16)} {var.kind} {var.type} {var.level} {var.address}\n')
    
    def writeProcedures(self):
        path = ''
        if __name__ == "__main__": path = '../'
        f = open(path+PRO_PATH, mode='w')
        for pro in self.procedures:
            f.write(f'{pro.name.rjust(16)} {pro.type} {pro.level} {pro.first} {pro.last}\n')
    
    def writeErrors(self):
        path = ''
        if __name__ == "__main__": path = '../'
        f = open(path+ERR_PATH, mode='w')
        for err in self.errors:
            f.write(err+'\n')
        
    @staticmethod
    def readTokens():
        path = ''
        if __name__ == "__main__": path = '../'
        f = open(path+DYD_PATH)
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