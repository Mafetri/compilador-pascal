# Predictive parser with file input for the given grammar
import sys
import re

# Global lookahead token and token stream
LAMlookahead = None
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
        sys.exit(f"Syntax error: expected {expected}, found {lookahead}")

def programa():
    """<programa> ::= program <identificador> ; <bloque> ."""
    global lookahead
    if lookahead == 'program':
        match('program')
        match('ident')
        match(';')
        bloque()
        match('.')
    else:
        sys.exit("Syntax error: expected 'program'")

def bloque():
    """<bloque> ::= [<declaraciones de variables>] [<declaracion de subrutinas>] <sentencia compuesta>"""
    global lookahead
    if lookahead == 'var':
        parte_de_declaraciones_de_variables()
    if lookahead in ['procedure', 'function']:
        declaracion_de_subrutinas()
    sentencia_compuesta()

def parte_de_declaraciones_de_variables():
    """<parte de declaraciones de variables> ::= var <declaracion de variables> {; <declaracion de variables> };"""
    global lookahead
    match('var')
    declaracion_de_variables()
    while lookahead == ';':
        match(';')
        if lookahead == 'ident':
            declaracion_de_variables()
        else:
            break
    if lookahead != 'begin':
        match(';')

def declaracion_de_variables():
    """<declaracion de variables> ::= <lista identificadores> : <tipo>"""
    global lookahead
    lista_identificadores()
    match(':')
    tipo()

def lista_identificadores():
    """<lista identificadores> ::= <identificador> { , <identificador> }"""
    global lookahead
    match('ident')
    while lookahead == ',':
        match(',')
        match('ident')

def tipo():
    """<tipo> ::= integer | boolean"""
    global lookahead
    if lookahead in ['integer', 'boolean']:
        match(lookahead)
    else:
        sys.exit("Syntax error: expected 'integer' or 'boolean'")

def declaracion_de_subrutinas():
    """<declaracion de subrutina> ::= { <declaracion de procedimiento> ; | <declaracion de funcion> ; }"""
    global lookahead
    while lookahead in ['procedure', 'function']:
        if lookahead == 'procedure':
            declaracion_de_procedimiento()
            match(';')
        elif lookahead == 'function':
            declaracion_de_funcion()
            match(';')

def declaracion_de_procedimiento():
    """<declaracion de procedimiento> ::= procedure <identificador> [ <parámetros formales> ] ; <bloque>"""
    global lookahead
    match('procedure')
    match('ident')
    if lookahead == '(':
        parámetros_formales()
    match(';')
    bloque()

def declaracion_de_funcion():
    """<declaracion de funcion> ::= function <identificador> [ <parámetros formales> ] : <tipo> ; <bloque>"""
    global lookahead
    match('function')
    match('ident')
    if lookahead == '(':
        parámetros_formales()
    match(':')
    tipo()
    match(';')
    bloque()

def parámetros_formales():
    """<parámetros formales> ::= ( <seccion de parámetros formales> { ; <seccion de parámetros formales> } )"""
    global lookahead
    match('(')
    seccion_de_parámetros_formales()
    while lookahead == ';':
        match(';')
        seccion_de_parámetros_formales()
    match(')')

def seccion_de_parámetros_formales():
    """<seccion de parámetros formales> ::= <lista de identificadores> : <tipo>"""
    global lookahead
    lista_identificadores()
    match(':')
    tipo()

def sentencia_compuesta():
    """<sentencia compuesta> ::= begin <sentencia> { ; <sentencia> } end"""
    global lookahead
    match('begin')
    sentencia()
    while lookahead == ';':
        match(';')
        sentencia()
    match('end')

def sentencia():
    """<sentencia> ::= <asignacion> | <llamada a procedimiento> | <sentencia compuesta> | 
                       <sentencia condicional> | <sentencia repetitiva> | <sentencia lectura> | 
                       <sentencia escritura>"""
    global lookahead
    if lookahead == 'ident':
        current_index = token_index 
        next_tok = tokens[current_index] if current_index < len(tokens) else None
        if next_tok == ':=':
            asignacion()
        elif next_tok == '(':
            llamada_a_procedimiento()
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
        sys.exit(f"Syntax error: invalid statement, found '{lookahead}'")


def asignacion():
    """<asignacion> ::= <variable> := <expresion>"""
    global lookahead
    variable()
    match(':=')
    expresion()

def variable():
    """<variable> ::= <identificador>"""
    global lookahead
    match('ident')

def llamada_a_procedimiento():
    """<llamada a procedimiento> ::= <identificador> [ ( <lista de expresiones> ) ]"""
    global lookahead
    match('ident')
    if lookahead == '(':
        match('(')
        lista_de_expresiones()
        match(')')

def sentencia_condicional():
    """<sentencia condicional> ::= if <expresion> then <sentencia> [ else <sentencia> ]"""
    global lookahead
    match('if')
    expresion()
    match('then')
    sentencia()
    # match(';')                                                                                          # AGREGUE ESTO PARA QUE FUNCIONEEEEEE
    if lookahead == 'else':
        match('else')
        sentencia()
        # print(token_index, lookahead)

def sentencia_repetitiva():
    """<sentencia repetitiva> ::= while <expresion> do <sentencia>"""
    global lookahead
    match('while')
    expresion()
    match('do')
    sentencia()

def sentencia_lectura():
    """<sentencia lectura> ::= read ( <identificador> )"""
    global lookahead
    match('read')
    match('(')
    match('ident')
    match(')')

def sentencia_escritura():
    """<sentencia escritura> ::= write ( <identificador> )"""
    global lookahead
    match('write')
    match('(')
    match('ident')
    match(')')

def lista_de_expresiones():
    """<lista de expresiones> ::= <expresion> { , <expresion> }"""
    global lookahead
    expresion()
    while lookahead == ',':
        match(',')
        expresion()

def expresion():
    """<expresion> ::= <expresion simple> [ <relacion> <expresion simple> ]"""
    global lookahead
    expresion_simple()
    if lookahead in ['=', '<>', '<', '>', '<=', '>=']:
        relacion()
        expresion_simple()

def relacion():
    """<relacion> ::= = | <> | < | > | <= | >="""
    global lookahead
    if lookahead in ['=', '<>', '<', '>', '<=', '>=']:
        match(lookahead)
    else:
        sys.exit("Syntax error: expected relational operator")

def expresion_simple():
    """<expresion simple> ::= [+|-] <termino> { (+|-|or) <termino> }"""
    global lookahead
    if lookahead in ['+', '-']:
        match(lookahead)
    termino()
    while lookahead in ['+', '-', 'or']:
        match(lookahead)
        termino()

def termino():
    """<termino> ::= <factor> { (*|div|and) <factor> }"""
    global lookahead
    factor()
    while lookahead in ['*', 'div', 'and']:
        match(lookahead)
        factor()

def factor():
    """<factor> ::= <identificador> | numero | <llamada a funcion> | ( <expresion> ) | 
                       not <factor> | true | false"""
    global lookahead, token_index, tokens
    if lookahead == 'ident':
        if token_index < len(tokens):
            next_tok = tokens[token_index]
            if next_tok == '(':
                llamada_a_funcion()
            else:
                match('ident')
        else:
            match('ident')
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
        sys.exit("Syntax error: invalid factor")


def llamada_a_funcion():
    """<llamada a funcion> ::= <identificador> [ ( <lista de expresiones> ) ]"""
    global lookahead
    match('ident')
    if lookahead == '(':
        match('(')
        lista_de_expresiones()
        match(')')