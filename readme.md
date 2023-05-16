# 编译原理实验

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
