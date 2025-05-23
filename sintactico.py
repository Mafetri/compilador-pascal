# Global lookahead token and token stream
lookahead = None
tokens = []
token_index = 0

def sintactico(token_list):
    global tokens, token_index, lookahead
    tokens = token_list
    token_index = 0
    lookahead = next_token()
    programa()

def next_token():
    """Fetch the next token from the token stream."""
    global token_index, tokens
    if token_index < len(tokens):
        token = tokens[token_index]
        token_index += 1
        return token
    return None

def match(expected):
    """Match the lookahead token with the expected terminal."""
    global lookahead
    if lookahead == expected:
        lookahead = next_token()
    else:
        raise SyntaxError(f"Syntax error: expected {expected}, found {lookahead}")

def programa():
    """<programa> ::= program <identificador> ; <bloque> ."""
    match('program')
    match('ident')
    match(';')
    bloque()
    match('.')

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
    match(';')
    if lookahead == 'ident':
        declaracion_de_variables()
        mas_declaraciones()

def declaracion_de_variables():
    """<declaracion de variables> ::= <lista identificadores> : <tipo>"""
    lista_identificadores()
    match(':')
    tipo()

def lista_identificadores():
    """<lista identificadores> ::= <identificador> <mas identificadores>"""
    match('ident')
    mas_identificadores()

def mas_identificadores():
    """<mas identificadores> ::= , <identificador> <mas identificadores> | λ"""
    if lookahead == ',':
        match(',')
        match('ident')
        mas_identificadores()

def tipo():
    """<tipo> ::= integer | boolean"""
    if lookahead in ['integer', 'boolean']:
        match(lookahead)
    else:
        raise SyntaxError("Syntax error: expected 'integer' or 'boolean'")

def parte_declaraciones_subrutinas():
    """<parte declaraciones subrutinas> ::= <declaracion de subrutina> <mas subrutinas>"""
    declaracion_de_subrutina()
    mas_subrutinas()

def mas_subrutinas():
    """<mas subrutinas> ::= ; <declaracion de subrutina> <mas subrutinas> | λ"""
    if lookahead == ';':
        match(';')
        declaracion_de_subrutina()
        mas_subrutinas()

def declaracion_de_subrutina():
    """<declaracion de subrutina> ::= <declaracion de procedimiento> | <declaracion de funcion>"""
    if lookahead == 'procedure':
        declaracion_de_procedimiento()
    elif lookahead == 'function':
        declaracion_de_funcion()
    else:
        raise SyntaxError("Syntax error: expected 'procedure' or 'function'")

def declaracion_de_procedimiento():
    """<declaracion de procedimiento> ::= procedure <identificador> <parte parametros formales> ; <bloque>"""
    match('procedure')
    match('ident')
    parte_parametros_formales()
    match(';')
    bloque()

def declaracion_de_funcion():
    """<declaracion de funcion> ::= function <identificador> <parte parametros formales> : <tipo> ; <bloque>"""
    match('function')
    match('ident')
    parte_parametros_formales()
    match(':')
    tipo()
    match(';')
    bloque()

def parte_parametros_formales():
    """<parte parametros formales> ::= ( <seccion de parametros formales> <mas secciones parametros> ) | λ"""
    if lookahead == '(':
        match('(')
        seccion_de_parametros_formales()
        mas_secciones_parametros()
        match(')')

def mas_secciones_parametros():
    """<mas secciones parametros> ::= ; <seccion de parametros formales> <mas secciones parametros> | λ"""
    while lookahead == ';':
        match(';')
        seccion_de_parametros_formales()

def seccion_de_parametros_formales():
    """<seccion de parametros formales> ::= <lista de identificadores> : <tipo>"""
    lista_identificadores()
    match(':')
    tipo()

def sentencia_compuesta():
    """<sentencia compuesta> ::= begin <sentencia> <mas sentencias> end"""
    match('begin')
    sentencia()
    mas_sentencias()
    match('end')

def mas_sentencias():
    """<mas sentencias> ::= ; <sentencia> <mas sentencias> | λ"""
    if lookahead == ';':
        match(';')
        sentencia()
        mas_sentencias()

def sentencia():
    """<sentencia> ::= <asignacion> | <llamada a procedimiento> | <sentencia compuesta> | 
                       <sentencia condicional> | <sentencia repetitiva> | <sentencia lectura> | 
                       <sentencia escritura>"""
    if lookahead == 'ident':
        # Look ahead to distinguish between assignment and procedure call
        next_idx = token_index
        if next_idx < len(tokens) and tokens[next_idx] == ':=':
            asignacion()
        else:
            llamada_a_procedimiento()
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
        raise SyntaxError(f"Syntax error: invalid statement, found '{lookahead}'")

def asignacion():
    """<asignacion> ::= <variable> := <expresion>"""
    variable()
    match(':=')
    expresion()

def variable():
    """<variable> ::= <identificador>"""
    match('ident')

def llamada_a_procedimiento():
    """<llamada a procedimiento> ::= <identificador> <parte parametros actuales>"""
    match('ident')
    parte_parametros_actuales()

def sentencia_condicional():
    """<sentencia condicional> ::= if <expresion> then <sentencia> <parte else>"""
    match('if')
    expresion()
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
    expresion()
    match('do')
    sentencia()

def sentencia_lectura():
    """<sentencia lectura> ::= read ( <identificador> )"""
    match('read')
    match('(')
    match('ident')
    match(')')

def sentencia_escritura():
    """<sentencia escritura> ::= write ( <identificador> )"""
    match('write')
    match('(')
    match('ident')
    match(')')

def parte_parametros_actuales():
    """<parte parametros actuales> ::= ( <lista de expresiones> ) | λ"""
    if lookahead == '(':
        match('(')
        lista_de_expresiones()
        match(')')

def lista_de_expresiones():
    """<lista de expresiones> ::= <expresion> <mas expresiones>"""
    expresion()
    mas_expresiones()

def mas_expresiones():
    """<mas expresiones> ::= , <expresion> <mas expresiones> | λ"""
    if lookahead == ',':
        match(',')
        expresion()
        mas_expresiones()

def expresion():
    """<expresion> ::= <expresion simple> <parte relacion>"""
    expresion_simple()
    parte_relacion()

def parte_relacion():
    """<parte relacion> ::= <relacion> <expresion simple> | λ"""
    if lookahead in ['=', '<>', '<', '>', '<=', '>=']:
        relacion()
        expresion_simple()

def relacion():
    """<relacion> ::= = | <> | < | > | <= | >="""
    if lookahead in ['=', '<>', '<', '>', '<=', '>=']:
        match(lookahead)
    else:
        raise SyntaxError("Syntax error: expected relational operator")

def expresion_simple():
    """<expresion simple> ::= <signo> <termino> <resto expresion simple> | <termino> <resto expresion simple>"""
    if lookahead in ['+', '-']:
        signo()
    termino()
    resto_expresion_simple()

def signo():
    """<signo> ::= + | -"""
    if lookahead in ['+', '-']:
        match(lookahead)
    else:
        raise SyntaxError("Syntax error: expected '+' or '-'")

def resto_expresion_simple():
    """<resto expresion simple> ::= <op aditivo> <termino> <resto expresion simple> | λ"""
    if lookahead in ['+', '-', 'or']:
        op_aditivo()
        termino()
        resto_expresion_simple()

def op_aditivo():
    """<op aditivo> ::= + | - | or"""
    if lookahead in ['+', '-', 'or']:
        match(lookahead)
    else:
        raise SyntaxError("Syntax error: expected additive operator")

def termino():
    """<termino> ::= <factor> <resto termino>"""
    factor()
    resto_termino()

def resto_termino():
    """<resto termino> ::= <op multiplicativo> <factor> <resto termino> | λ"""
    if lookahead in ['*', 'div', 'and']:
        op_multiplicativo()
        factor()
        resto_termino()

def op_multiplicativo():
    """<op multiplicativo> ::= * | div | and"""
    if lookahead in ['*', 'div', 'and']:
        match(lookahead)
    else:
        raise SyntaxError("Syntax error: expected multiplicative operator")

def factor():
    """<factor> ::= <identificador> <factor identificador> | numero | ( <expresion> ) | not <factor> | true | false"""
    if lookahead == 'ident':
        match('ident')
        factor_identificador()
    elif lookahead == 'numero':
        match('numero')
    elif lookahead == '(':
        match('(')
        expresion()
        match(')')
    elif lookahead == 'not':
        match('not')
        factor()
    elif lookahead in ['true', 'false']:
        match(lookahead)
    else:
        raise SyntaxError("Syntax error: invalid factor")

def factor_identificador():
    """<factor identificador> ::= <parte parametros actuales> | λ"""
    if lookahead == '(':
        parte_parametros_actuales()

def llamada_a_funcion():
    """<llamada a funcion> ::= <identificador> <parte parametros actuales>"""
    match('ident')
    parte_parametros_actuales()