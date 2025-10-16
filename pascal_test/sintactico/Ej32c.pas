program prueba; { Archivo Prueba C&I: EJ32C.PAS }
var
  a,b:integer;
  c:boolean;

 begin
   read( a, b ); 
   c:= true;
   case c of
     0,5,6 : write( a );
     1 : write( a + b );
     2 : write( b );
     3 : write( b - 5 );
     else
         write( -a ); 
 end.

