from semantico import AnalizadorSemantico

semantico = AnalizadorSemantico()

# Variables globales para almacenar información del token actual
lexer = None
lookahead = None
lookahead_value = None
lookahead_line = None
lookahead_col = None

def sintactico(lexer_instance):
    """Initialize the global lexer and start parsing."""
    global lexer, lookahead, lookahead_value, lookahead_line, lookahead_col
    lexer = lexer_instance
    token_info = next_token()
    lookahead, lookahead_value, lookahead_line, lookahead_col = token_info
    programa()

def next_token():
    """Fetch the next token from the global lexer."""
    global lexer
    return lexer.next_token()

def match(expected):
    """Match the lookahead token with the expected terminal."""
    global lookahead, lookahead_value, lookahead_line, lookahead_col
    if lookahead == expected:
        token_info = next_token()
        lookahead, lookahead_value, lookahead_line, lookahead_col = token_info
    else:
        raise SyntaxError(
            f"Syntax error at line {lookahead_line}, column {lookahead_col}: "
            f"expected '{expected}', found '{lookahead}'"
        )

def programa():
    """<programa> ::= program <identificador> ; <bloque> ."""
    match('program')
    program_name = lookahead_value
    match('ident')
    semantico.tabla_simbolos.insertar(program_name, 'program', 'programa', lookahead_col, lookahead_line)
    match('punto_coma')
    bloque()
    match('punto')

def bloque():
    """<bloque> ::= <parte declaraciones variables> <parte declaraciones subrutinas> <sentencia compuesta>
       <bloque> ::= <parte declaraciones variables> <sentencia compuesta>
       <bloque> ::= <parte declaraciones subrutinas> <sentencia compuesta>
       <bloque> ::= <sentencia compuesta>"""
    if lookahead == 'var':
        parte_declaraciones_variables()
        if lookahead in ['procedure', 'function']:
            parte_declaraciones_subrutinas()
        sentencia_compuesta()
    elif lookahead in ['procedure', 'function']:
        parte_declaraciones_subrutinas()
        sentencia_compuesta()
    else:
        sentencia_compuesta()

def parte_declaraciones_variables():
    """<parte declaraciones variables> ::= var <declaracion de variables> <mas declaraciones>"""
    match('var')
    declaracion_de_variables()
    mas_declaraciones()

def mas_declaraciones():
    """<mas declaraciones> ::= ; <declaracion de variables> <mas declaraciones> | ;"""
    match('punto_coma')
    if lookahead == 'ident':
        declaracion_de_variables()
        mas_declaraciones()

def declaracion_de_variables():
    """<declaracion de variables> ::= <lista identificadores> : <tipo>"""
    variables = lista_identificadores()
    match('asignacion_de_tipo')
    tipo_var = tipo()
    
    for var in variables:
        semantico.tabla_simbolos.insertar(var, tipo_var, 'variable', lookahead_col, lookahead_line)

def lista_identificadores():
    """<lista identificadores> ::= <identificador> <mas identificadores>"""
    variables = [lookahead_value]
    match('ident')
    variables.extend(mas_identificadores())
    return variables

def mas_identificadores():
    """<mas identificadores> ::= , <identificador> <mas identificadores> | λ"""
    variables = []
    if lookahead == 'coma':
        match('coma')
        variables.append(lookahead_value)
        match('ident')
        variables.extend(mas_identificadores())
    return variables

def tipo():
    """<tipo> ::= integer | boolean"""
    if lookahead in ['integer', 'boolean']:
        tipo_val = lookahead
        match(lookahead)
        return tipo_val
    else:
        raise SyntaxError(
            f"Syntax error at line {lookahead_line}, column {lookahead_col}: "
            "expected 'integer' or 'boolean'"
        )

def parte_declaraciones_subrutinas():
    """<parte declaraciones subrutinas> ::= <declaracion de subrutina> <mas subrutinas>"""
    declaracion_de_subrutina()
    mas_subrutinas()

def mas_subrutinas():
    """<mas subrutinas> ::= ; <declaracion de subrutina> <mas subrutinas> | λ"""
    if lookahead == 'punto_coma':
        match('punto_coma')
        declaracion_de_subrutina()
        mas_subrutinas()

def declaracion_de_subrutina():
    """<declaracion de subrutina> ::= <declaracion de procedimiento> | <declaracion de funcion>"""
    if lookahead == 'procedure':
        declaracion_de_procedimiento()
    elif lookahead == 'function':
        declaracion_de_funcion()
    else:
        raise SyntaxError(
            f"Syntax error at line {lookahead_line}, column {lookahead_col}: "
            "expected 'procedure' or 'function'"
        )

def declaracion_de_procedimiento():
    """<declaracion de procedimiento> ::= procedure <identificador> <parte parametros formales> ; <bloque>"""
    match('procedure')
    proc_name = lookahead_value
    match('ident')
    
    # Entrar nuevo ámbito
    semantico.tabla_simbolos.entrar_ambito(proc_name)
    semantico.funcion_actual = proc_name
    
    # Procesar parámetros
    parametros = parte_parametros_formales()
    semantico.tabla_simbolos.insertar(proc_name, 'void', 'procedimiento', lookahead_col, lookahead_line, 'global', parametros)
    
    match('punto_coma')
    bloque()
    
    # Salir ámbito
    semantico.tabla_simbolos.salir_ambito()
    semantico.funcion_actual = None

def declaracion_de_funcion():
    """<declaracion de funcion> ::= function <identificador> <parte parametros formales> : <tipo> ; <bloque>"""
    match('function')
    func_name = lookahead_value
    match('ident')
    
    # Entrar nuevo ámbito
    semantico.tabla_simbolos.entrar_ambito(func_name)
    semantico.funcion_actual = func_name
    
    # Procesar parámetros
    parametros = parte_parametros_formales()
    match('asignacion_de_tipo')
    return_type = tipo()
    semantico.verificar_tipo(return_type, lookahead_col, lookahead_line)
    
    semantico.tabla_simbolos.insertar(func_name, return_type, 'funcion', lookahead_col, lookahead_line, 'global', parametros)
    
    match('punto_coma')
    bloque()
    
    # Salir ámbito
    semantico.tabla_simbolos.salir_ambito()
    semantico.funcion_actual = None

def parte_parametros_formales():
    """<parte parametros formales> ::= ( <seccion de parametros formales> <mas secciones parametros> ) | λ"""
    parametros = []
    if lookahead == 'parentesis_izq':
        match('parentesis_izq')
        parametros.extend(seccion_de_parametros_formales())
        parametros.extend(mas_secciones_parametros())
        match('parentesis_der')
    return parametros

def mas_secciones_parametros():
    """<mas secciones parametros> ::= ; <seccion de parametros formales> <mas secciones parametros> | λ"""
    parametros = []
    while lookahead == 'punto_coma':
        match('punto_coma')
        parametros.extend(seccion_de_parametros_formales())
    return parametros

def seccion_de_parametros_formales():
    """<seccion de parametros formales> ::= <lista de identificadores> : <tipo>"""
    variables = lista_identificadores()
    match('asignacion_de_tipo')
    tipo_param = tipo()
    
    parametros = []
    for var in variables:
        semantico.tabla_simbolos.insertar(var, tipo_param, 'variable', lookahead_col, lookahead_line)
        parametros.append({'nombre': var, 'tipo': tipo_param})
    
    return parametros

def sentencia_compuesta():
    """<sentencia compuesta> ::= begin <sentencia> <mas sentencias> end"""
    match('begin')
    sentencia()
    mas_sentencias()
    match('end')

def mas_sentencias():
    """<mas sentencias> ::= ; <sentencia> <mas sentencias> | λ"""
    if lookahead == 'punto_coma':
        match('punto_coma')
        sentencia()
        mas_sentencias()

def sentencia():
    """<sentencia> ::= <asignacion> | <llamada a procedimiento> | <sentencia compuesta> | 
                       <sentencia condicional> | <sentencia repetitiva> | <sentencia lectura> | 
                       <sentencia escritura>"""
    if lookahead == 'ident':
        sentencia_ident()
    elif lookahead == 'begin':
        sentencia_compuesta()
    elif lookahead == 'if':
        sentencia_condicional()
    elif lookahead == 'while':
        sentencia_repetitiva()
    elif lookahead == 'read':
        sentencia_lectura()
    elif lookahead == 'write':
        sentencia_escritura()
    else:
        raise SyntaxError(
            f"Syntax error at line {lookahead_line}, column {lookahead_col}: "
            f"invalid statement, found '{lookahead}'"
        )

def sentencia_ident():
    """<sentencia ident> ::= := <expresion> | <parte de parametros actuales>"""
    ident_name = lookahead_value
    match('ident')
    
    if lookahead == 'asignacion':
        # Es una asignación
        variable = semantico.verificar_declaracion(lookahead_line, lookahead_col, ident_name, 'variable')
        match('asignacion')
        expr_type = expresion()
        semantico.verificar_asignacion(lookahead_line, lookahead_col, variable, expr_type)
    else:
        # Es una llamada a procedimiento/función
        funcion = semantico.verificar_declaracion(lookahead_line, lookahead_col, ident_name)
        if funcion['categoria'] not in ['procedimiento', 'funcion']:
            raise SyntaxError(f"Semantic error at line {lookahead_line}, column {lookahead_col}: '{ident_name}' is not a procedure or function")
        
        parametros_tipos = parte_parametros_actuales()
        
        if funcion['categoria'] == 'funcion':
            semantico.verificar_llamada_funcion(lookahead_line, lookahead_col, funcion, parametros_tipos)
        else:
            semantico.verificar_llamada_procedimiento(lookahead_line, lookahead_col, funcion, parametros_tipos)

def sentencia_condicional():
    """<sentencia condicional> ::= if <expresion> then <sentencia> <parte else>"""
    match('if')
    expr_type = expresion()
    if expr_type != 'boolean':
        raise SyntaxError(f"Semantic error at line {lookahead_line}, column {lookahead_col}: the 'if' condition must be boolean")
    match('then')
    sentencia()
    parte_else()

def parte_else():
    """<parte else> ::= else <sentencia> | λ"""
    if lookahead == 'else':
        match('else')
        sentencia()

def sentencia_repetitiva():
    """<sentencia repetitiva> ::= while <expresion> do <sentencia>"""
    match('while')
    expr_type = expresion()
    if expr_type != 'boolean':
        raise SyntaxError(f"Semantic error at line {lookahead_line}, column {lookahead_col}: the 'while' condition must be boolean")
    match('do')
    sentencia()

def sentencia_lectura():
    """<sentencia lectura> ::= read ( <identificador> )"""
    match('read')
    match('parentesis_izq')
    var_name = lookahead_value
    match('ident')
    variable = semantico.verificar_declaracion(lookahead_line, lookahead_col, var_name, 'variable')
    if variable['tipo'] != 'integer':
        raise SyntaxError(f"Semantic error at line {lookahead_line}, column {lookahead_col}: only integer variables can be read, '{var_name}' is {variable['tipo']} type")
    match('parentesis_der')

def sentencia_escritura():
    """<sentencia escritura> ::= write ( <identificador> )"""
    match('write')
    match('parentesis_izq')
    var_name = lookahead_value
    match('ident')
    semantico.verificar_declaracion(lookahead_line, lookahead_col, var_name, 'variable')
    match('parentesis_der')

def parte_parametros_actuales():
    """<parte parametros actuales> ::= ( <resto parametros actuales> | λ"""
    if lookahead == 'parentesis_izq':
        match('parentesis_izq')
        return resto_parametros_actuales()
    return []

def resto_parametros_actuales():
    """<resto parametros actuales> ::= ) | <lista de expresiones> )"""
    if lookahead == 'parentesis_der':
        match('parentesis_der')
        return []
    else:
        parametros_tipos = lista_de_expresiones()
        match('parentesis_der')
        return parametros_tipos

def lista_de_expresiones():
    """<lista de expresiones> ::= <expresion> <mas expresiones>"""
    tipos = [expresion()]
    tipos.extend(mas_expresiones())
    return tipos

def mas_expresiones():
    """<mas expresiones> ::= , <expresion> <mas expresiones> | λ"""
    tipos = []
    if lookahead == 'coma':
        match('coma')
        tipos.append(expresion())
        tipos.extend(mas_expresiones())
    return tipos

def expresion():
    """<expresion> ::= <expresion simple> <parte relacion>"""
    tipo_simple = expresion_simple()
    return parte_relacion(tipo_simple)

def parte_relacion(tipo_izq):
    """<parte relacion> ::= <relacion> <expresion simple> | λ"""
    if lookahead in ['=', '<>', '<', '>', '<=', '>=']:
        op = relacion()
        tipo_der = expresion_simple()
        return semantico.verificar_operacion_binaria(lookahead_line, lookahead_col, op, tipo_izq, tipo_der)
    return tipo_izq

def relacion():
    """<relacion> ::= = | <> | < | > | <= | >="""
    if lookahead in ['=', '<>', '<', '>', '<=', '>=']:
        op = lookahead
        match(lookahead)
        return op
    else:
        raise SyntaxError(
            f"Syntax error at line {lookahead_line}, column {lookahead_col}: "
            f"expected relational operator"
        )

def expresion_simple():
    """<expresion simple> ::= <signo> <termino> <resto expresion simple> | <termino> <resto expresion simple>"""
    if lookahead in ['+', '-']:
        op = signo()
        tipo_term = termino()
        tipo_final = semantico.verificar_operacion_unaria(lookahead_line, lookahead_col, op, tipo_term)
    else:
        tipo_final = termino()
        
    return resto_expresion_simple(tipo_final)

def signo():
    """<signo> ::= + | -"""
    if lookahead in ['+', '-']:
        op = lookahead
        match(lookahead)
        return op
    else:
        raise SyntaxError(
            f"Syntax error at line {lookahead_line}, column {lookahead_col}: "
            "expected '+' or '-'"
        )

def resto_expresion_simple(tipo_actual):
    """<resto expresion simple> ::= <op aditivo> <termino> <resto expresion simple> | λ"""
    if lookahead in ['+', '-', 'or']:
        op = op_aditivo()
        tipo_term = termino()
        nuevo_tipo = semantico.verificar_operacion_binaria(lookahead_line, lookahead_col, op, tipo_actual, tipo_term)
        return resto_expresion_simple(nuevo_tipo)
    return tipo_actual

def op_aditivo():
    """<op aditivo> ::= + | - | or"""
    if lookahead in ['+', '-', 'or']:
        op = lookahead
        match(lookahead)
        return op
    else:
        raise SyntaxError(
            f"Syntax error at line {lookahead_line}, column {lookahead_col}: "
            "expected additive operator"
        )

def termino():
    """<termino> ::= <factor> <resto termino>"""
    tipo_fact = factor()
    return resto_termino(tipo_fact)

def resto_termino(tipo_actual):
    """<resto termino> ::= <op multiplicativo> <factor> <resto termino> | λ"""
    if lookahead in ['*', 'div', 'and']:
        op = op_multiplicativo()
        tipo_fact = factor()
        nuevo_tipo = semantico.verificar_operacion_binaria(lookahead_line, lookahead_col, op, tipo_actual, tipo_fact)
        return resto_termino(nuevo_tipo)
    return tipo_actual

def op_multiplicativo():
    """<op multiplicativo> ::= * | div | and"""
    if lookahead in ['*', 'div', 'and']:
        op = lookahead
        match(lookahead)
        return op
    else:
        raise SyntaxError(
            f"Syntax error at line {lookahead_line}, column {lookahead_col}: "
            "expected multiplicative operator"
        )

def factor():
    """<factor> ::= <identificador> <factor identificador> | numero | ( <expresion> ) | not <factor> | true | false"""
    if lookahead == 'ident':
        ident_name = lookahead_value
        match('ident')
        return factor_identificador(ident_name)
    elif lookahead == 'numero':
        match('numero')
        return 'integer'
    elif lookahead == 'parentesis_izq':
        match('parentesis_izq')
        tipo_expr = expresion()
        match('parentesis_der')
        return tipo_expr
    elif lookahead == 'not':
        match('not')
        tipo_fact = factor()
        return semantico.verificar_operacion_unaria(lookahead_line, lookahead_col, 'not', tipo_fact)
    elif lookahead in ['true', 'false']:
        valor = lookahead
        match(lookahead)
        return 'boolean'
    else:
        raise SyntaxError(
            f"Syntax error at line {lookahead_line}, column {lookahead_col}: "
            "invalid factor"
        )

def factor_identificador(ident_name):
    """<factor identificador> ::= <parte parametros actuales> | λ"""
    if lookahead == 'parentesis_izq':
        # Es una llamada a función
        funcion = semantico.verificar_declaracion(lookahead_line, lookahead_col, ident_name, 'funcion')
        parametros_tipos = parte_parametros_actuales()
        return semantico.verificar_llamada_funcion(lookahead_line, lookahead_col, funcion, parametros_tipos)
    else:
        # Es una variable
        variable = semantico.verificar_declaracion(lookahead_line, lookahead_col, ident_name, 'variable')
        return variable['tipo']