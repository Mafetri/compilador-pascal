program Test3;

var
  a, b: integer;

begin
  a := 1;   { cambia a falso }
  b := -1;

  if a = 0 then
  begin
    if b > 0 then
      write(9);
  end
  else
    write(3);   { else externo }
end.