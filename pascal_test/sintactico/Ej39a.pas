program prueba; { Archivo Prueba C&I: EJ39A.PAS }
var
  a,b:integer;
  c:boolean;

 begin
   read( a, b ); 
   c:= true;
   case a of   
     0,1 : ;
     2 : write( a );
   end;
 end.

