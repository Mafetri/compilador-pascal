program Test4;

var
  x, y, z: integer;

begin
  x := 1;
  y := 2;
  z := -5;

  if x = 1 then
    if y = 2 then
      if z > 0 then
        write(9)
      else
        write(1)   { else de z }
    else
      write(2)     { else de y }
  else
    write(3);      { else de x }
end.