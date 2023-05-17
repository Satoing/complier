# 编译原理实验

## 实验内容

求 $n!$ 的程序:
```pascal
begin
  integer k;
  integer function F(n);
  begin
    integer n;
    if n <= 0 then F:= 1
    else F:= n * F(n-1)
  end;
  read(m);
  k:= F(m);
  write(k)
end
```

据此设计一个极小语言，并：

1. 完成词法分析器
2. 完成递归下降的语法分析器

## 运行

1. 词法分析器+语法分析器一起运行：
  ```bash
  python3 app.py
  ```
2. 单独运行词法/语法分析器：
  ```bash
  cd src
  python3 myLexer.py
  python3 myParser.py
  ```
3. 输出文件在output目录里面