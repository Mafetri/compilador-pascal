Program ConductorDePrueba;
Var a: integer;
    local: integer;

procedure XX;

	function pru(r:integer):integer;
	var local: boolean;
	begin
	  if (r= 0) then pru:= 1
	  else
	     local:= r-1>2; 
 

	    a:= pru(a);
            pru:= 33;
	end;

begin
    a:= pru(a);
    {pru:= 33; }
end;

Function factorial(r:integer):integer;
begin
   
  {a:= pru(a); }     {----> acá da error tb}

  if r = 1 then
    factorial := 1
  else
    factorial := r * factorial(r-1);
end;

Begin

  {a:= pru(a);  }   {----> acá da error tb}


  a:= local;
  pru:= 33;
  local:= pru(33);
  a := factorial(3);
  write(a);
End.
