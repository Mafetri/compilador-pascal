program FibRec;
var res, n: integer;
function fib(n: integer): integer;
begin
    if n <= 1 then
        fib := n
    else
        fib := fib(n-1) + fib(n-2)
end

begin
	Read(n);
	res := fib(n);
	write(res);
end.