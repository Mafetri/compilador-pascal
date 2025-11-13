"""
Módulo de Árbol de Sintaxis Abstracta (AST) para el compilador Pascal.
Define las clases de nodos que representan la estructura del programa.
"""

class NodoAST:
    """Clase base para todos los nodos del AST."""
    def __init__(self, tipo_nodo):
        self.tipo_nodo = tipo_nodo

# --- Nodos de Expresiones ---

class NodoIdentificador(NodoAST):
    """Nodo para identificadores (variables)."""
    def __init__(self, nombre):
        super().__init__('identificador')
        self.nombre = nombre

class NodoNumero(NodoAST):
    """Nodo para literales numéricos."""
    def __init__(self, valor):
        super().__init__('numero')
        self.valor = valor

class NodoBooleano(NodoAST):
    """Nodo para literales booleanos (true/false)."""
    def __init__(self, valor):
        super().__init__('booleano')
        self.valor = valor  # 'true' o 'false'

class NodoOperacionBinaria(NodoAST):
    """Nodo para operaciones binarias (+, -, *, div, and, or, <, >, etc.)."""
    def __init__(self, izquierda, operador, derecha):
        super().__init__('operacion_binaria')
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

class NodoOperacionUnaria(NodoAST):
    """Nodo para operaciones unarias (-, not)."""
    def __init__(self, operador, operando):
        super().__init__('operacion_unaria')
        self.operador = operador
        self.operando = operando

class NodoExpresion(NodoAST):
    """Nodo wrapper para expresiones entre paréntesis."""
    def __init__(self, expresion):
        super().__init__('expresion')
        self.expresion = expresion

class NodoLlamadaFuncion(NodoAST):
    """Nodo para llamadas a funciones."""
    def __init__(self, nombre, parametros):
        super().__init__('llamada_funcion')
        self.nombre = nombre
        self.parametros = parametros or []

# --- Nodos de Sentencias ---

class NodoAsignacion(NodoAST):
    """Nodo para asignaciones: id := expresion"""
    def __init__(self, variable, expresion):
        super().__init__('asignacion')
        self.variable = variable  # NodoIdentificador o string con nombre
        self.expresion = expresion

class NodoBloque(NodoAST):
    """Nodo para bloques de sentencias (begin ... end)."""
    def __init__(self, sentencias):
        super().__init__('bloque')
        self.sentencias = sentencias or []

class NodoIf(NodoAST):
    """Nodo para sentencias condicionales: if E then S1 [else S2]"""
    def __init__(self, condicion, cuerpo_true, cuerpo_false=None):
        super().__init__('if')
        self.condicion = condicion
        self.cuerpo_true = cuerpo_true
        self.cuerpo_false = cuerpo_false

class NodoWhile(NodoAST):
    """Nodo para bucles: while E do S"""
    def __init__(self, condicion, cuerpo):
        super().__init__('while')
        self.condicion = condicion
        self.cuerpo = cuerpo

class NodoLlamadaProcedimiento(NodoAST):
    """Nodo para llamadas a procedimientos."""
    def __init__(self, nombre, parametros):
        super().__init__('llamada_procedimiento')
        self.nombre = nombre
        self.parametros = parametros or []

class NodoRead(NodoAST):
    """Nodo para sentencias de lectura: read(id)"""
    def __init__(self, variable):
        super().__init__('read')
        self.variable = variable  # NodoIdentificador o string con nombre

class NodoWrite(NodoAST):
    """Nodo para sentencias de escritura: write(E)"""
    def __init__(self, expresion):
        super().__init__('write')
        self.expresion = expresion

class NodoPrograma(NodoAST):
    """Nodo raíz del programa."""
    def __init__(self, nombre, declaraciones, bloque_principal):
        super().__init__('programa')
        self.nombre = nombre
        self.declaraciones = declaraciones
        self.bloque = bloque_principal

class NodoDeclaracionProcedimiento(NodoAST):
    """Nodo para la *declaración* de un procedimiento."""
    def __init__(self, nombre, parametros, declaraciones_internas, bloque_cuerpo):
        super().__init__('declaracion_procedimiento')
        self.nombre = nombre
        self.parametros = parametros # Lista de dicts {'nombre': 'w', 'tipo': 'boolean'}
        self.declaraciones_internas = declaraciones_internas # Para anidamiento
        self.bloque_cuerpo = bloque_cuerpo # NodoBloque del begin...end

class NodoDeclaracionFuncion(NodoAST):
    """Nodo para la *declaración* de una función."""
    def __init__(self, nombre, parametros, tipo_retorno, declaraciones_internas, bloque_cuerpo):
        super().__init__('declaracion_funcion')
        self.nombre = nombre
        self.parametros = parametros
        self.tipo_retorno = tipo_retorno
        self.declaraciones_internas = declaraciones_internas
        self.bloque_cuerpo = bloque_cuerpo