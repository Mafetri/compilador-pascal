program prueba; { Archivo Prueba C&I: EJ30D.PAS }
var
  a,b:integer;
  c:boolean;

 begin
   a:= 9; 
   c:= true;
   while ( a < 10 > 5 )  do
     if a > 10 
       then 
         begin
           a := 0 ;
           c := false;
         end
       else 
         begin
           a := a + 1;
           write( a );
         end
 end.

