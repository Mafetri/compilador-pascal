program prueba; { Archivo Prueba C&I: EJ41C.PAS }
var
  a,b:integer;
  c:boolean;

funcion suma( var x, y: integer) : integer;
begin
  suma:= x + y;
end;

 begin
   read( a, b ); 
   c:= true;
   write( a + suma( a, b) );
 end.

