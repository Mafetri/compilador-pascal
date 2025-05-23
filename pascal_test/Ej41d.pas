program prueba; { Archivo Prueba C&I: EJ41D.PAS }
var
  a,b:integer;
  c:boolean;

procedure suma( var x, y: integer);
var a: integer;
begin
  a:= x + y;
  write( a );
end;

 begin
   read( a, b ); 
   c:= true;
   write( a + suma( a, b) );
 end.

