program SumaRec;
var res, n: integer;
function sum(n: integer): integer;
begin
    if n = 0 then
        sum := 0
    else
        sum := n + sum(n - 1)
end

begin
	Read(n);
	res := sum(n);
    write(res);
end.