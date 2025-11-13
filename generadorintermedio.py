# (Asumo que tabla_simbolos.py ahora tiene la versión actualizada de arriba)
from tabla_simbolos import TablaSimbolos

class GeneradorCodigoIntermedio:
    """
    Genera Código de Tres Direcciones (3AC) en forma de Cuádruplas.
    Funciona sobre un AST ya validado por el AnalizadorSemantico.
    """
    def __init__(self, tabla_simbolos: TablaSimbolos):
        # Recibe la tabla de símbolos YA POBLADA por el AnalizadorSemantico
        self.tabla_simbolos = tabla_simbolos
        self.codigo = []  # Lista de cuádruplas
        self.contador_temporales = 0
        self.contador_etiquetas = 0

    def nuevo_temporal(self) -> str:
        """Crea un nuevo nombre de variable temporal (newtemp)."""
        temp = f"t{self.contador_temporales}"
        self.contador_temporales += 1
        # Opcionalmente, agregar a la TS (como sugiere el PDF)
        # self.tabla_simbolos.insertar(temp, 'temporal', 'temporal', 0, 0, ambito='temporal')
        return temp

    def nueva_etiqueta(self) -> str:
        """Crea una nueva etiqueta para saltos (newlabel)."""
        etiqueta = f"L{self.contador_etiquetas}"
        self.contador_etiquetas += 1
        return etiqueta

    def emitir(self, op: str, arg1: str | None, arg2: str | None, res: str | None):
        """Añade una nueva cuádrupla a la lista de código."""
        cuadrupla = {'op': op, 'arg1': arg1, 'arg2': arg2, 'res': res}
        self.codigo.append(cuadrupla)

    def imprimir_codigo(self):
        """Muestra el código intermedio generado de forma legible."""
        print("\n--- CÓDIGO INTERMEDIO GENERADO ---")
        for i, cuad in enumerate(self.codigo):
            if cuad['op'] == 'label':
                # Imprime etiquetas en su propia línea para claridad
                print(f"\n{cuad['res']}:")
            elif cuad['op'] == ':=':
                print(f"  {i:03d}: {cuad['res']} := {cuad['arg1']}")
            elif cuad['op'] == 'goto':
                 print(f"  {i:03d}: goto {cuad['res']}")
            elif 'if_' in cuad['op']: # Saltos condicionales
                op_salto = cuad['op'].replace('if_', '') # ej: '<', '>=', '=='
                print(f"  {i:03d}: if {cuad['arg1']} {op_salto} {cuad['arg2']} goto {cuad['res']}")
            elif cuad['op'] == 'param':
                print(f"  {i:03d}: param {cuad['arg1']}")
            elif cuad['op'] == 'call':
                 print(f"  {i:03d}: {cuad['res'] or ''} := call {cuad['arg1']}, {cuad['arg2']}")
            elif cuad['op'] == 'read':
                print(f"  {i:03d}: read {cuad['res']}")
            elif cuad['op'] == 'write':
                print(f"  {i:03d}: write {cuad['arg1']}")
            elif cuad['op'] in ['uminus', 'not']: # Operadores unarios
                print(f"  {i:03d}: {cuad['res']} := {cuad['op']} {cuad['arg1']}")
            else: # Operaciones binarias
                print(f"  {i:03d}: {cuad['res']} := {cuad['arg1']} {cuad['op']} {cuad['arg2']}")
        print("----------------------------------\n")
        
    # --- Generadores de Sentencias (S) ---
    
    def generar(self, nodo):
        """Punto de entrada principal para generar código desde un nodo AST."""
        if not nodo:
            return

        # Asumo que el parser asigna un 'tipo_nodo' a cada nodo del AST
        metodo_generador = f"generar_{nodo.tipo_nodo}"
        if hasattr(self, metodo_generador):
            # Llama al método específico (ej: generar_asignacion(nodo))
            getattr(self, metodo_generador)(nodo)
        else:
            raise ValueError(f"No hay generador para el tipo de nodo: {nodo.tipo_nodo}")
    
    def generar_programa(self, nodo_programa):
        """Genera código para el programa completo."""
        self.generar_bloque(nodo_programa.bloque)

    def generar_bloque(self, nodo_bloque):
        """Genera código para una secuencia de sentencias."""
        for sentencia in nodo_bloque.sentencias:
            self.generar(sentencia)

    def generar_asignacion(self, nodo_asignacion):
        """Genera código para S -> id := E"""
        # 1. Generar código para la expresión E.
        lugar_expresion = self.generar_expresion(nodo_asignacion.expresion)
        
        # 2. Emitir la asignación
        # Obtener el nombre de la variable (puede ser NodoIdentificador o string)
        nombre_var = nodo_asignacion.variable.nombre if hasattr(nodo_asignacion.variable, 'nombre') else nodo_asignacion.variable
        self.emitir(':=', lugar_expresion, None, nombre_var)

    def generar_if(self, nodo_if):
        """Genera código para if E then S1 [else S2]"""
        etiqueta_true = self.nueva_etiqueta()
        etiqueta_false = self.nueva_etiqueta()
        
        # Si hay 'else', S.next es una nueva etiqueta al final.
        # Si no hay 'else', S.next es E.false.
        etiqueta_fin = self.nueva_etiqueta() if nodo_if.cuerpo_false else etiqueta_false

        # 1. Generar código para la condición (E.code)
        # Esto genera saltos a E.true (etiqueta_true) o E.false (etiqueta_false)
        self.generar_booleano_flujo(nodo_if.condicion, etiqueta_true, etiqueta_false)

        # 2. Código del 'then' (S1.code)
        self.emitir('label', None, None, etiqueta_true) # gen(E.true ':')
        self.generar(nodo_if.cuerpo_true)

        if nodo_if.cuerpo_false:
            # 3. Salto para evitar el 'else'
            self.emitir('goto', None, None, etiqueta_fin) # gen('goto' S.next)
            
            # 4. Código del 'else' (S2.code)
            self.emitir('label', None, None, etiqueta_false) # gen(E.false ':')
            self.generar(nodo_if.cuerpo_false)
            
            # 5. Etiqueta final
            self.emitir('label', None, None, etiqueta_fin) # S.next:
        else:
            # 3. Si no hay 'else', la etiqueta 'false' es el final
            self.emitir('label', None, None, etiqueta_false) # E.false es S.next

    def generar_while(self, nodo_while):
        """Genera código para while E do S1"""
        etiqueta_inicio = self.nueva_etiqueta()  # S.begin
        etiqueta_true = self.nueva_etiqueta()   # E.true
        etiqueta_fin = self.nueva_etiqueta()    # E.false / S.next
        
        # 1. Etiqueta de inicio del bucle
        self.emitir('label', None, None, etiqueta_inicio) # gen(S.begin ':')
        
        # 2. Código de la condición
        self.generar_booleano_flujo(nodo_while.condicion, etiqueta_true, etiqueta_fin)
        
        # 3. Código del cuerpo (S1.code)
        self.emitir('label', None, None, etiqueta_true) # gen(E.true ':')
        self.generar(nodo_while.cuerpo)
        
        # 4. Volver al inicio
        self.emitir('goto', None, None, etiqueta_inicio) # gen('goto' S.begin)
        
        # 5. Etiqueta de salida del bucle
        self.emitir('label', None, None, etiqueta_fin) # S.next:

    def generar_llamada_procedimiento(self, nodo_call):
        """Genera código para call id(Elist)"""
        param_lugares = []
        if nodo_call.parametros:
            for param in nodo_call.parametros:
                param_lugares.append(self.generar_expresion(param))
        
        # Emitir sentencias 'param' en orden inverso (convención de llamadas)
        for param_lugar in reversed(param_lugares):
            self.emitir('param', param_lugar, None, None)
        
        # Emitir la llamada
        num_params = len(param_lugares)
        self.emitir('call', nodo_call.nombre, num_params, None)
    
    def generar_llamada_funcion(self, nodo_call):
        """Genera código para id := funcion(Elist)"""
        param_lugares = []
        if nodo_call.parametros:
            for param in nodo_call.parametros:
                param_lugares.append(self.generar_expresion(param))
        
        # Emitir sentencias 'param' en orden inverso
        for param_lugar in reversed(param_lugares):
            self.emitir('param', param_lugar, None, None)
        
        # Crear temporal para el resultado
        temp_resultado = self.nuevo_temporal()
        num_params = len(param_lugares)
        self.emitir('call', nodo_call.nombre, num_params, temp_resultado)
        
        return temp_resultado
    
    def generar_read(self, nodo_read):
        """Genera código para read(id)"""
        nombre_var = nodo_read.variable.nombre if hasattr(nodo_read.variable, 'nombre') else nodo_read.variable
        self.emitir('read', None, None, nombre_var)
    
    def generar_write(self, nodo_write):
        """Genera código para write(E)"""
        lugar_expr = self.generar_expresion(nodo_write.expresion)
        self.emitir('write', lugar_expr, None, None)
    
    # --- Generadores de Expresiones (E) ---
    
    def generar_expresion(self, nodo_expresion):
        """
        Genera código para expresiones y devuelve el lugar (temporal o constante).
        Diferencia entre operadores aritméticos y lógicos/relacionales:
        - Aritméticos (+, -, *, div): genera cuádrupla aritmética normal
        - Lógicos/Relacionales (and, or, not, <, >, =, etc.): genera código con saltos
          para asignar 1 (true) o 0 (false) a un temporal (Representación Numérica)
        """
        if not nodo_expresion:
            return None
        
        tipo_nodo = getattr(nodo_expresion, 'tipo_nodo', None)
        
        # Si es un nodo hoja (identificador, número o booleano)
        if tipo_nodo == 'identificador':
            return nodo_expresion.nombre
        elif tipo_nodo == 'numero':
            return str(nodo_expresion.valor)
        elif tipo_nodo == 'booleano':
            # Convertir 'true' a '1' y 'false' a '0' para representación numérica
            return '1' if nodo_expresion.valor == 'true' else '0'
        
        # Si es una operación binaria
        if tipo_nodo == 'operacion_binaria':
            op = nodo_expresion.operador
            
            # Operadores aritméticos: generar cuádrupla aritmética normal
            if op in ['+', '-', '*', 'div']:
                lugar1 = self.generar_expresion(nodo_expresion.izquierda)
                lugar2 = self.generar_expresion(nodo_expresion.derecha)
                temp = self.nuevo_temporal()
                self.emitir(op, lugar1, lugar2, temp)
                return temp
            
            # Operadores lógicos/relacionales: generar código con saltos (Representación Numérica)
            elif op in ['and', 'or', '<', '>', '<=', '>=', '=', '<>']:
                return self.generar_expresion_booleana_numerica(nodo_expresion)
            
            else:
                raise ValueError(f"Operador binario no reconocido: {op}")
        
        # Si es una operación unaria
        if tipo_nodo == 'operacion_unaria':
            op = nodo_expresion.operador
            
            # Operador aritmético unario: generar cuádrupla aritmética
            if op == '-':
                lugar = self.generar_expresion(nodo_expresion.operando)
                temp = self.nuevo_temporal()
                self.emitir('uminus', lugar, None, temp)
                return temp
            
            # Operador lógico unario: generar código con saltos (Representación Numérica)
            elif op == 'not':
                return self.generar_expresion_booleana_numerica(nodo_expresion)
            
            else:
                raise ValueError(f"Operador unario no reconocido: {op}")
        
        # Si es una llamada a función
        if tipo_nodo == 'llamada_funcion':
            return self.generar_llamada_funcion(nodo_expresion)
        
        # Si es una expresión entre paréntesis
        if tipo_nodo == 'expresion':
            return self.generar_expresion(nodo_expresion.expresion)
        
        # Por defecto, intentar generar recursivamente
        raise ValueError(f"No se puede generar código para el tipo de expresión: {tipo_nodo}")
    
    def generar_expresion_booleana_numerica(self, nodo_expresion):
        """
        Genera código para expresiones booleanas que retornan valores numéricos (1 o 0).
        Usa Representación Numérica: genera saltos condicionales para asignar 1 (true) o 0 (false).
        """
        temp_resultado = self.nuevo_temporal()
        etiqueta_true = self.nueva_etiqueta()
        etiqueta_false = self.nueva_etiqueta()
        etiqueta_fin = self.nueva_etiqueta()
        
        # Generar código de flujo de control para la expresión booleana
        self.generar_booleano_flujo(nodo_expresion, etiqueta_true, etiqueta_false)
        
        # Etiqueta para cuando la expresión es verdadera: asignar 1
        self.emitir('label', None, None, etiqueta_true)
        self.emitir(':=', '1', None, temp_resultado)
        self.emitir('goto', None, None, etiqueta_fin)
        
        # Etiqueta para cuando la expresión es falsa: asignar 0
        self.emitir('label', None, None, etiqueta_false)
        self.emitir(':=', '0', None, temp_resultado)
        
        # Etiqueta final
        self.emitir('label', None, None, etiqueta_fin)
        
        return temp_resultado
    
    def generar_booleano_flujo(self, nodo_expresion, etiqueta_true, etiqueta_false):
        """
        Genera código para expresiones booleanas con flujo de control.
        E -> E and E | E or E | not E | E relop E | id | numero | (E)
        """
        if not nodo_expresion:
            return
        
        tipo_nodo = getattr(nodo_expresion, 'tipo_nodo', None)
        
        # Si es un identificador booleano
        if tipo_nodo == 'identificador':
            # Verificar que sea booleano y hacer salto condicional
            temp = self.nuevo_temporal()
            self.emitir(':=', nodo_expresion.nombre, None, temp)
            self.emitir('if_!=', temp, 'false', etiqueta_true)
            self.emitir('goto', None, None, etiqueta_false)
            return
        
        # Operadores lógicos con evaluación cortocircuitada
        if tipo_nodo == 'operacion_binaria':
            op = nodo_expresion.operador
            
            if op == 'and':
                # E.true = E1.true, E.false = nueva_etiqueta que apunta a E2.false
                etiqueta_intermedia = self.nueva_etiqueta()
                self.generar_booleano_flujo(nodo_expresion.izquierda, etiqueta_intermedia, etiqueta_false)
                self.emitir('label', None, None, etiqueta_intermedia)
                self.generar_booleano_flujo(nodo_expresion.derecha, etiqueta_true, etiqueta_false)
                return
            
            elif op == 'or':
                # E.false = E1.false, E.true = nueva_etiqueta que apunta a E2.true
                etiqueta_intermedia = self.nueva_etiqueta()
                self.generar_booleano_flujo(nodo_expresion.izquierda, etiqueta_true, etiqueta_intermedia)
                self.emitir('label', None, None, etiqueta_intermedia)
                self.generar_booleano_flujo(nodo_expresion.derecha, etiqueta_true, etiqueta_false)
                return
            
            elif op in ['<', '>', '<=', '>=', '=', '<>']:
                # Operadores relacionales
                lugar1 = self.generar_expresion(nodo_expresion.izquierda)
                lugar2 = self.generar_expresion(nodo_expresion.derecha)
                
                # Mapear operadores a operaciones de salto condicional
                op_salto = op
                if op == '<>':
                    op_salto = '!='
                elif op == '=':
                    op_salto = '=='
                
                self.emitir(f'if_{op_salto}', lugar1, lugar2, etiqueta_true)
                self.emitir('goto', None, None, etiqueta_false)
                return
        
        # Operador not
        if tipo_nodo == 'operacion_unaria' and nodo_expresion.operador == 'not':
            # Intercambiar true y false
            self.generar_booleano_flujo(nodo_expresion.operando, etiqueta_false, etiqueta_true)
            return
        
        # Si es una expresión entre paréntesis
        if tipo_nodo == 'expresion':
            self.generar_booleano_flujo(nodo_expresion.expresion, etiqueta_true, etiqueta_false)
            return
        
        # Por defecto, tratar como expresión aritmética y comparar con 0 o false
        lugar = self.generar_expresion(nodo_expresion)
        # Asumir que si no es 0/false, es verdadero
        self.emitir('if_!=', lugar, '0', etiqueta_true)
        self.emitir('goto', None, None, etiqueta_false)