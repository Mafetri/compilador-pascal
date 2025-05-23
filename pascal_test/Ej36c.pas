program prueba; { Archivo Prueba C&I: EJ36C.PAS }
var
  a,b:integer;
  c:boolean;

 begin
   read( a, b ); 
   c:= true;
   case a of   
     1 : a := a + 10;
     2 : write( a );
   end;
 end.

