program ContarDigitos;
var res, n, original, digitos: integer;

begin
	read(n);
    original := n;
    digitos := 0;

    while n > 0 do
    begin
        n := n div 10;
        digitos := digitos + 1
    end;

    write(digitos)
end.
