class Cursor():
    def __init__(self, src: str):
        self.position = 0
        self.source = src
    
    # 获取接下来应该读取的字符
    def current(self):
        return self.source[self.position]
    
    # 获取接下来应该读取的字符，并指针前移
    def consume(self):
        current = self.current()
        self.position += 1
        return current
    
    # 判断文件是否读取完
    def isOpen(self):
        return self.position < len(self.source)
       
    def __repr__(self):
        return f'position: {self.position}\nsource:\n{self.source}'