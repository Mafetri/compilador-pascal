program prueba; { Archivo Prueba C&I: EJ35A.PAS }
var
  a,b:integer;
  c:boolean;

 begin
   read( a, b ); 
   c:= true;
   case c of 
     true : write( a );
     false : write( a + b );
     else 
         write( b );
   end;
 end.

