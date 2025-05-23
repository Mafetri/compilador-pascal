program prueba; { Archivo Prueba C&I: EJ27C.PAS }
var
  a,b:integer;
  c:boolean;

 begin
   a:= 9; 
   c:= true;
   if ( c )
     then 
        a := a + 10 ;
     else
        a := a - 10 ;
        write( a ) ;
 end.

