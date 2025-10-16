program prueba ;{ Archivo Prueba C&I: EJ22D.PAS }
var
  a,b:integer;

function algo(a: integer): integer;
begin
  write ( a );
  algo := a + 1;
end;

 begin
   a:= 9; 
   b:= algo();
 end.

