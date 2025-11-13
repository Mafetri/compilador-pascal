from tabla_simbolos import TablaSimbolos

class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = TablaSimbolos()
        self.ambito_actual = "global"
        self.funcion_actual = None
        self.tipo_retorno_actual = None  # Track current function return type
        self.retorno_encontrado = False  # Track if return assignment was found
        
    def verificar_tipo(self, tipo, col, row ):
        if tipo not in ['integer', 'boolean']:
            raise SyntaxError(f"Semantic error at line {row}, column {col}: type '{tipo}' not valid")
            
    def verificar_declaracion(self, row, col, nombre, categoria=None):
        simbolo = self.tabla_simbolos.buscar(nombre)
        if simbolo is None:
            raise SyntaxError(f"Semantic error at line {row}, column {col}: '{nombre}' not declared")
        if categoria and simbolo['categoria'] != categoria:
            raise SyntaxError(f"Semantic error at line {row}, column {col}: '{nombre}' is not a {categoria}")
        return simbolo
        
    def verificar_asignacion(self, row, col, variable, expresion_tipo):
        if variable['tipo'] != expresion_tipo:
            raise SyntaxError(f"Semantic error at line {row}, column {col}: can not assign '{expresion_tipo}' to variable '{variable['nombre']}' type '{variable['tipo']}'")
            
    def verificar_operacion_binaria(self, row, col, op, tipo1, tipo2):
        if op in ['+', '-', '*', 'div']:
            if tipo1 != 'integer' or tipo2 != 'integer':
                raise SyntaxError(f"Semantic error at line {row}, column {col}: operation '{op}' requires integer operators")
            return 'integer'
        elif op in ['=', '<>', '<', '>', '<=', '>=']:
            if tipo1 != tipo2:
                raise SyntaxError(f"Semantic error at line {row}, column {col}: operation '{op}' requires operators of the same type")
            if op in ['<', '>', '<=', '>='] and tipo1 == 'boolean':
                raise SyntaxError(f"Semantic error at line {row}, column {col}: operation '{op}' not allowed for boolean types")
            return 'boolean'
        elif op in ['and', 'or']:
            if tipo1 != 'boolean' or tipo2 != 'boolean':
                raise SyntaxError(f"Semantic error at line {row}, column {col}: operation '{op}' requires boolean operators")
            return 'boolean'
        else:
            raise SyntaxError(f"Semantic error at line {row}, column {col}: operator '{op}' not recognized")
            
    def verificar_operacion_unaria(self, row, col, op, tipo):
        if op == 'not':
            if tipo != 'boolean':
                raise SyntaxError(f"Semantic error at line {row}, column {col}: operation 'not' requires boolean operator")
            return 'boolean'
        elif op in ['+', '-']:
            if tipo != 'integer':
                raise SyntaxError(f"Semantic error at line {row}, column {col}: operation '{op}' requires integer operator")
            return 'integer'
            
    def verificar_llamada_funcion(self, row, col, funcion, parametros_actuales):
        if len(funcion['parametros']) != len(parametros_actuales):
            raise SyntaxError(f"Semantic error at line {row}, column {col}: function '{funcion['nombre']}' requires {len(funcion['parametros'])} parameters, {len(parametros_actuales)} were given")
            
        for i, (param_formal, param_actual) in enumerate(zip(funcion['parametros'], parametros_actuales)):
            if param_formal['tipo'] != param_actual:
                raise SyntaxError(f"Semantic error at line {row}, column {col}: parameter {i+1} of function '{funcion['nombre']}' must be '{param_formal['tipo']}', but '{param_actual}' was provided")
                
        return funcion['tipo']
    
    def verificar_llamada_procedimiento(self, row, col, procedimiento, parametros_actuales):
        if len(procedimiento['parametros']) != len(parametros_actuales):
            raise SyntaxError(
                f"Semantic error at line {row}, column {col}: "
                f"procedure '{procedimiento['nombre']}' requires {len(procedimiento['parametros'])} parameters, "
                f"{len(parametros_actuales)} were given"
            )

        for i, (param_formal, param_actual) in enumerate(zip(procedimiento['parametros'], parametros_actuales)):
            if param_formal['tipo'] != param_actual:
                raise SyntaxError(
                    f"Semantic error at line {row}, column {col}: "
                    f"parameter {i+1} of procedure '{procedimiento['nombre']}' must be '{param_formal['tipo']}', "
                    f"but '{param_actual}' was provided"
                )

    def verificar_retorno_funcion(self, row, col, tipo_expresion):
        """Verify function return assignment"""
        if not self.funcion_actual:
            raise SyntaxError(f"Semantic error at line {row}, column {col}: can not assign to function name outside function body")
        
        if self.tipo_retorno_actual != tipo_expresion:
            raise SyntaxError(f"Semantic error at line {row}, column {col}: function '{self.funcion_actual}' returns '{self.tipo_retorno_actual}', but assigned expression is '{tipo_expresion}'")
        
        # Mark that we found at least one return assignment
        self.retorno_encontrado = True