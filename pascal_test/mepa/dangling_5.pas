program Test5;

var
  x, y, z: integer;

begin
  x := 1;
  y := 2;
  z := -5;

  if x = 1 then
  begin
    if y = 2 then
      if z > 0 then
        write(9);
  end
  else
    write(3);    { else asociado a x }
end.
