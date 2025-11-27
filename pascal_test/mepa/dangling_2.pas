program Test2;

var
  a, b: integer;

begin
  a := 0;
  b := -1;

  if a = 0 then
  begin
    if b > 0 then
      write(9);
  end
  else
    write(3);   { else asociado al if de a }
end.