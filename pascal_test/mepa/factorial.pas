program TestFactorial;
var n, res: integer;

function factorial(n: integer): integer;
begin
    if n = 0 then
        Factorial := 1
    else
        Factorial := n * Factorial(n - 1)
end

begin
	Read(n);
	res := factorial(n);
    Write(res);
end.
