program prueba; { Archivo Prueba C&I: EJ31.PAS }
var
  a,b:integer;
  c:boolean;

 begin
   a:= 9; 
   c:= true;
   while ( a < 10 ) do
     begin
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
       write( a );
     end;
 end.

