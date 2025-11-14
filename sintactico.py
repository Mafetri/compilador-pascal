from semantico import AnalizadorSemantico
from ast import (
    NodoAsignacion, NodoBloque, NodoIf, NodoWhile,
    NodoLlamadaProcedimiento, NodoLlamadaFuncion,
    NodoRead, NodoWrite, NodoPrograma,
    NodoIdentificador, NodoNumero, NodoBooleano,
    NodoOperacionBinaria, NodoOperacionUnaria, NodoExpresion,
    NodoDeclaracionProcedimiento, NodoDeclaracionFuncion
)

semantico = AnalizadorSemantico()
# Variable global para almacenar el AST raíz
ast_raiz = None

def inferir_tipo(nodo):
    """Infiere el tipo de un nodo AST."""
    if nodo is None:
        return None
    
    # Si el nodo ya tiene un atributo tipo, usarlo
    if hasattr(nodo, 'tipo'):
        return nodo.tipo
    
    # Inferir según el tipo de nodo
    if nodo.tipo_nodo == 'identificador':
        # Buscar en tabla de símbolos
        simbolo = semantico.tabla_simbolos.buscar(nodo.nombre)
        if simbolo:
            return simbolo['tipo']
        return None
    elif nodo.tipo_nodo == 'numero':
        return 'integer'
    elif nodo.tipo_nodo == 'booleano':
        return 'boolean'
    elif nodo.tipo_nodo == 'operacion_binaria':
        # Inferir desde los operandos
        tipo_izq = inferir_tipo(nodo.izquierda)
        tipo_der = inferir_tipo(nodo.derecha)
        if tipo_izq and tipo_der:
            # Usar verificación semántica para obtener el tipo resultante
            try:
                return semantico.verificar_operacion_binaria(0, 0, nodo.operador, tipo_izq, tipo_der)
            except:
                return None
    elif nodo.tipo_nodo == 'operacion_unaria':
        tipo_op = inferir_tipo(nodo.operando)
        if tipo_op:
            try:
                return semantico.verificar_operacion_unaria(0, 0, nodo.operador, tipo_op)
            except:
                return None
    elif nodo.tipo_nodo == 'expresion':
        return inferir_tipo(nodo.expresion)
    elif nodo.tipo_nodo == 'llamada_funcion':
        # El tipo ya debería estar en el nodo
        if hasattr(nodo, 'tipo'):
            return nodo.tipo
        return None
    
    return None

# Variables globales para almacenar información del token actual
lexer = None
lookahead = None
lookahead_value = None
lookahead_line = None
lookahead_col = None

def sintactico(lexer_instance):
    """Initialize the global lexer and start parsing."""
    global lexer, lookahead, lookahead_value, lookahead_line, lookahead_col, ast_raiz
    lexer = lexer_instance
    token_info = next_token()
    lookahead, lookahead_value, lookahead_line, lookahead_col = token_info
    ast_raiz = programa()
    return ast_raiz

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
    declaraciones_sub, nodo_bloque_principal = bloque()
    match('punto')
    return NodoPrograma(program_name, declaraciones_sub, nodo_bloque_principal)

def bloque():
    """<bloque> ::= <parte declaraciones variables> <parte declaraciones subrutinas> <sentencia compuesta>
       <bloque> ::= <parte declaraciones variables> <sentencia compuesta>
       <bloque> ::= <parte declaraciones subrutinas> <sentencia compuesta>
       <bloque> ::= <sentencia compuesta>"""
    declaraciones_subrutinas = []
    
    if lookahead == 'var':
        parte_declaraciones_variables()
        if lookahead in ['procedure', 'function']:
            declaraciones_subrutinas = parte_declaraciones_subrutinas() 
    elif lookahead in ['procedure', 'function']:
        declaraciones_subrutinas = parte_declaraciones_subrutinas()
    
    nodo_sentencia_compuesta = sentencia_compuesta()
    
    return declaraciones_subrutinas, nodo_sentencia_compuesta

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
    nodos = [declaracion_de_subrutina()]
    nodos.extend(mas_subrutinas())
    return nodos

def mas_subrutinas():
    """<mas subrutinas> ::= ; <declaracion de subrutina> <mas subrutinas> | λ"""
    nodos = []
    if lookahead == 'punto_coma':
        match('punto_coma')
        nodos.append(declaracion_de_subrutina())
        nodos.extend(mas_subrutinas())
    return nodos

def declaracion_de_subrutina():
    """<declaracion de subrutina> ::= <declaracion de procedimiento> | <declaracion de funcion>"""
    if lookahead == 'procedure':
        return declaracion_de_procedimiento()
    elif lookahead == 'function':
        return declaracion_de_funcion()
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
    
    # bloque() ahora devuelve una tupla
    declaraciones_internas, nodo_bloque_proc = bloque()
    
    # Salir ámbito
    semantico.tabla_simbolos.salir_ambito()
    semantico.funcion_actual = None
    
    # Crear y devolver el nuevo nodo AST
    return NodoDeclaracionProcedimiento(proc_name, parametros, declaraciones_internas, nodo_bloque_proc)

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
    
    # Store return type for verification
    semantico.tipo_retorno_actual = return_type
    semantico.retorno_encontrado = False  # Track if return assignment was found
    
    semantico.tabla_simbolos.insertar(func_name, return_type, 'funcion', lookahead_col, lookahead_line, 'global', parametros)
    semantico.tabla_simbolos.insertar(func_name, return_type, 'variable', lookahead_col, lookahead_line)
    match('punto_coma')

    declaraciones_internas, nodo_bloque_func = bloque()    

    # Verify that return assignment was found
    if not semantico.retorno_encontrado:
        raise SyntaxError(f"Semantic error: function '{func_name}' must assign a value to its name for return")
    
    # Salir ámbito
    semantico.tabla_simbolos.salir_ambito()
    semantico.funcion_actual = None
    semantico.tipo_retorno_actual = None

    return NodoDeclaracionFuncion(func_name, parametros, return_type, declaraciones_internas, nodo_bloque_func)

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
    sentencias = [sentencia()]
    sentencias.extend(mas_sentencias())
    match('end')
    return NodoBloque(sentencias)

def mas_sentencias():
    """<mas sentencias> ::= ; <sentencia> <mas sentencias> | λ"""
    sentencias = []
    if lookahead == 'punto_coma':
        match('punto_coma')
        if lookahead != 'end':  # No hay más sentencias si encontramos 'end'
            sentencias.append(sentencia())
            sentencias.extend(mas_sentencias())
    return sentencias

def sentencia():
    """<sentencia> ::= <asignacion> | <llamada a procedimiento> | <sentencia compuesta> | 
                       <sentencia condicional> | <sentencia repetitiva> | <sentencia lectura> | 
                       <sentencia escritura>"""
    if lookahead == 'ident':
        return sentencia_ident()
    elif lookahead == 'begin':
        return sentencia_compuesta()
    elif lookahead == 'if':
        return sentencia_condicional()
    elif lookahead == 'while':
        return sentencia_repetitiva()
    elif lookahead == 'read':
        return sentencia_lectura()
    elif lookahead == 'write':
        return sentencia_escritura()
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
        # Function return assignment (e.g., f := expr inside function f)
        if semantico.funcion_actual and ident_name == semantico.funcion_actual:
            # Function return assignment
            match('asignacion')
            simbolo_var = semantico.verificar_declaracion(lookahead_line, lookahead_col, ident_name, 'variable')
            simbolo_var['nombre_original_funcion'] = semantico.funcion_actual
            nodo_expr = expresion()
            expr_type = getattr(nodo_expr, 'tipo', inferir_tipo(nodo_expr))
            semantico.verificar_retorno_funcion(lookahead_line, lookahead_col, expr_type)
            return NodoAsignacion(NodoIdentificador(ident_name), nodo_expr)
        else:
            # Regular variable assignment
            variable = semantico.verificar_declaracion(lookahead_line, lookahead_col, ident_name, 'variable')
            match('asignacion')
            nodo_expr = expresion()
            expr_type = getattr(nodo_expr, 'tipo', inferir_tipo(nodo_expr))
            semantico.verificar_asignacion(
                lookahead_line, lookahead_col, variable, expr_type
            )
            return NodoAsignacion(NodoIdentificador(ident_name), nodo_expr)
    else:
        # Es una llamada a procedimiento/función
        funcion = semantico.verificar_declaracion(lookahead_line, lookahead_col, ident_name)
        if funcion['categoria'] not in ['procedimiento', 'funcion']:
            raise SyntaxError(
                f"Semantic error at line {lookahead_line}, column {lookahead_col}: "
                f"'{ident_name}' is not a procedure or function"
            )

        # Get parameter nodes
        nodos_parametros = parte_parametros_actuales()
        parametros_tipos = [inferir_tipo(p) for p in nodos_parametros]

        if funcion['categoria'] == 'funcion':
            semantico.verificar_llamada_funcion(
                lookahead_line, lookahead_col, funcion, parametros_tipos
            )
            return NodoLlamadaFuncion(ident_name, nodos_parametros)
        else:
            semantico.verificar_llamada_procedimiento(
                lookahead_line, lookahead_col, funcion, parametros_tipos
            )
            return NodoLlamadaProcedimiento(ident_name, nodos_parametros)


def sentencia_condicional():
    """<sentencia condicional> ::= if <expresion> then <sentencia> <parte else>"""
    match('if')
    nodo_condicion = expresion()
    expr_type = inferir_tipo(nodo_condicion)
    if expr_type != 'boolean':
        raise SyntaxError(f"Semantic error at line {lookahead_line}, column {lookahead_col}: the 'if' condition must be boolean")
    match('then')
    nodo_cuerpo_true = sentencia()
    nodo_cuerpo_false = parte_else()
    return NodoIf(nodo_condicion, nodo_cuerpo_true, nodo_cuerpo_false)

def parte_else():
    """<parte else> ::= else <sentencia> | λ"""
    if lookahead == 'else':
        match('else')
        return sentencia()
    return None

def sentencia_repetitiva():
    """<sentencia repetitiva> ::= while <expresion> do <sentencia>"""
    match('while')
    nodo_condicion = expresion()
    expr_type = inferir_tipo(nodo_condicion)
    if expr_type != 'boolean':
        raise SyntaxError(f"Semantic error at line {lookahead_line}, column {lookahead_col}: the 'while' condition must be boolean")
    match('do')
    nodo_cuerpo = sentencia()
    return NodoWhile(nodo_condicion, nodo_cuerpo)

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
    return NodoRead(NodoIdentificador(var_name))

def sentencia_escritura():
    """<sentencia escritura> ::= write ( <identificador> | <numero> )"""
    match('write')
    match('parentesis_izq')

    if lookahead == 'ident':
        var_name = lookahead_value
        match('ident')
        semantico.verificar_declaracion(lookahead_line, lookahead_col, var_name, 'variable')
        nodo_expr = NodoIdentificador(var_name)
    elif lookahead == 'numero':
        num_value = lookahead_value
        match('numero')
        nodo_expr = NodoNumero(int(num_value))
    else:
        raise SyntaxError(f"Se esperaba identificador o número en línea {lookahead_line}, columna {lookahead_col}")

    match('parentesis_der')
    return NodoWrite(nodo_expr)

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
        nodos_parametros = lista_de_expresiones()
        match('parentesis_der')
        return nodos_parametros

def lista_de_expresiones():
    """<lista de expresiones> ::= <expresion> <mas expresiones>"""
    nodos = [expresion()]
    nodos.extend(mas_expresiones())
    return nodos

def mas_expresiones():
    """<mas expresiones> ::= , <expresion> <mas expresiones> | λ"""
    nodos = []
    if lookahead == 'coma':
        match('coma')
        nodos.append(expresion())
        nodos.extend(mas_expresiones())
    return nodos

def expresion():
    """<expresion> ::= <expresion simple> <parte relacion>"""
    nodo_simple = expresion_simple()
    return parte_relacion(nodo_simple)

def parte_relacion(nodo_izq):
    """<parte relacion> ::= <relacion> <expresion simple> | λ"""
    if lookahead in ['=', '<>', '<', '>', '<=', '>=']:
        op = relacion()
        nodo_der = expresion_simple()
        tipo_izq = inferir_tipo(nodo_izq)
        tipo_der = inferir_tipo(nodo_der)
        tipo_resultado = semantico.verificar_operacion_binaria(lookahead_line, lookahead_col, op, tipo_izq, tipo_der)
        nodo_resultado = NodoOperacionBinaria(nodo_izq, op, nodo_der)
        nodo_resultado.tipo = tipo_resultado
        return nodo_resultado
    return nodo_izq

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
        nodo_term = termino()
        tipo_term = inferir_tipo(nodo_term)
        tipo_final = semantico.verificar_operacion_unaria(lookahead_line, lookahead_col, op, tipo_term)
        nodo_unario = NodoOperacionUnaria(op, nodo_term)
        nodo_unario.tipo = tipo_final
        nodo_final = nodo_unario
    else:
        nodo_final = termino()
        
    return resto_expresion_simple(nodo_final)

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

def resto_expresion_simple(nodo_actual):
    """<resto expresion simple> ::= <op aditivo> <termino> <resto expresion simple> | λ"""
    if lookahead in ['+', '-', 'or']:
        op = op_aditivo()
        nodo_term = termino()
        tipo_actual = inferir_tipo(nodo_actual)
        tipo_term = inferir_tipo(nodo_term)
        nuevo_tipo = semantico.verificar_operacion_binaria(lookahead_line, lookahead_col, op, tipo_actual, tipo_term)
        nodo_binario = NodoOperacionBinaria(nodo_actual, op, nodo_term)
        nodo_binario.tipo = nuevo_tipo
        return resto_expresion_simple(nodo_binario)
    return nodo_actual

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
    nodo_fact = factor()
    return resto_termino(nodo_fact)

def resto_termino(nodo_actual):
    """<resto termino> ::= <op multiplicativo> <factor> <resto termino> | λ"""
    if lookahead in ['*', 'div', 'and']:
        op = op_multiplicativo()
        nodo_fact = factor()
        tipo_actual = inferir_tipo(nodo_actual)
        tipo_fact = inferir_tipo(nodo_fact)
        nuevo_tipo = semantico.verificar_operacion_binaria(lookahead_line, lookahead_col, op, tipo_actual, tipo_fact)
        nodo_binario = NodoOperacionBinaria(nodo_actual, op, nodo_fact)
        nodo_binario.tipo = nuevo_tipo
        return resto_termino(nodo_binario)
    return nodo_actual

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
        num_value = lookahead_value
        match('numero')
        nodo = NodoNumero(int(num_value))
        nodo.tipo = 'integer'
        return nodo
    elif lookahead == 'parentesis_izq':
        match('parentesis_izq')
        nodo_expr = expresion()
        match('parentesis_der')
        return NodoExpresion(nodo_expr)
    elif lookahead == 'not':
        match('not')
        nodo_fact = factor()
        tipo_fact = inferir_tipo(nodo_fact)
        tipo_resultado = semantico.verificar_operacion_unaria(lookahead_line, lookahead_col, 'not', tipo_fact)
        nodo_unario = NodoOperacionUnaria('not', nodo_fact)
        nodo_unario.tipo = tipo_resultado
        return nodo_unario
    elif lookahead in ['true', 'false']:
        valor = lookahead
        match(lookahead)
        nodo = NodoBooleano(valor)
        nodo.tipo = 'boolean'
        return nodo
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
        nodos_parametros = parte_parametros_actuales()
        parametros_tipos = [inferir_tipo(p) for p in nodos_parametros]
        tipo_resultado = semantico.verificar_llamada_funcion(lookahead_line, lookahead_col, funcion, parametros_tipos)
        nodo = NodoLlamadaFuncion(ident_name, nodos_parametros)
        nodo.tipo = tipo_resultado
        return nodo
    else:
        # Es una variable
        variable = semantico.verificar_declaracion(lookahead_line, lookahead_col, ident_name, 'variable')
        nodo = NodoIdentificador(ident_name)
        nodo.tipo = variable['tipo']
        return nodo