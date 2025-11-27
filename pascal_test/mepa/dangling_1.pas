program Test1;

var
  a, b: integer;

begin
  a := 0;
  b := -1;

  if a = 0 then
    if b > 0 then
      write(9)
    else
      write(1);   { else asociado al if de b }
end.