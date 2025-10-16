program prueba; { Archivo Prueba C&I: EJ27A.PAS }
var
  a,b:integer;
  c:boolean;

 begin
   a:= 9; 
   c:= true;
   if ( c )
     then 
        write( a ) ;
        a := a + 10 ;
     else
        a := a - 10 ;
 end.

