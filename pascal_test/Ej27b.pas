program prueba; { Archivo Prueba C&I: EJ27B.PAS }
var
  a,b:integer;
  c:boolean;

 begin
   a:= 9; 
   c:= true;
   if ( c )
        write( a ) ;
     then 
        a := a + 10 ;
     else
        a := a - 10 ;
 end.

