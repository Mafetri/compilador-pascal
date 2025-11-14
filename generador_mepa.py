from tabla_simbolos import TablaSimbolos
from ast import * 

class GeneradorMEPA:
    """
    Genera código MEPA (Máquina de Ejecución de PASCAL) a partir de un AST
    y una Tabla de Símbolos ya poblada.
    """
    def __init__(self, tabla_simbolos: TablaSimbolos):
        self.tabla_simbolos = tabla_simbolos
        self.codigo_mepa = []  # Lista de líneas de código MEPA
        self.contador_etiquetas = 0
        
        # Estructuras para almacenar la información de direccionamiento MEPA
        # Se llenarán durante el pre-cálculo
        self.info_niveles = {}     # map: {ambito_nombre: nivel_lexico}
        self.info_offsets = {}     # map: {clave_simbolo_unica: offset}
        self.info_locales = {}     # map: {ambito_nombre: num_variables_locales}
        self.info_params = {}      # map: {ambito_nombre: num_parametros}
        
        # Estado de la visita de generación de código
        self.ambito_actual_gen = "global"
        self.nivel_actual_gen = 0

    def nueva_etiqueta(self) -> str:
        """Crea una nueva etiqueta para saltos (newlabel)."""
        etiqueta = f"L{self.contador_etiquetas}"
        self.contador_etiquetas += 1
        return etiqueta

    def emitir(self, instruccion: str, *operandos):
        """Añade una instrucción MEPA al código."""
        if operandos:
            # Formatea operandos como "nivel,offset" o "etiqueta"
            op_str = ", ".join(map(str, operandos))
            self.codigo_mepa.append(f"  {instruccion} {op_str}")
        else:
            self.codigo_mepa.append(f"  {instruccion}")

    def emitir_etiqueta(self, etiqueta: str):
        """Añade una etiqueta MEPA al código."""
        self.codigo_mepa.append(f"{etiqueta} NADA")

    def imprimir_codigo(self):
        """Muestra el código MEPA generado de forma legible."""
        for linea in self.codigo_mepa:
            print(linea.strip())

    def obtener_codigo(self):
        """Devuelve el código MEPA como un único string."""
        return "\n".join(linea.strip() for linea in self.codigo_mepa)

    # --- PASO 1: PRE-CÁLCULO DE NIVELES Y DESPLAZAMIENTOS ---
    
    def precalculo(self, nodo_raiz: NodoPrograma):
        """
        Punto de entrada para la primera pasada. Recorre el AST para 
        asignar niveles léxicos y desplazamientos (offsets) a todos
        los símbolos.
        """
        # Inicializar nivel global
        self.info_niveles['global'] = 0
        
        # Procesar variables globales primero
        offset_local = 0
        for clave, simbolo in self.tabla_simbolos.tabla.items():
            if simbolo['ambito'] == 'global' and simbolo['categoria'] == 'variable':
                self.info_offsets[clave] = offset_local
                offset_local += 1
        self.info_locales['global'] = offset_local
        
        # Ahora procesar recursivamente
        self._precalculo_recursivo(nodo_raiz, 0, "global")


    def _precalculo_recursivo(self, nodo, nivel: int, ambito: str):
        """
        Visitor recursivo para la primera pasada (Pre-cálculo).
        """
        if not nodo:
            return

        tipo_nodo = getattr(nodo, 'tipo_nodo', None)
        
        # Registra el nivel para el ámbito actual
        self.info_niveles[ambito] = nivel
        
        # Asegurarse de que el ámbito esté en la lista de ámbitos de la tabla de símbolos
        if ambito not in self.tabla_simbolos.ambitos and ambito != "global":
            self.tabla_simbolos.ambitos.append(ambito)
        
        if tipo_nodo == 'programa':
            # Las variables globales ya fueron procesadas, ahora procesar subrutinas
            if nodo.declaraciones:
                for decl in nodo.declaraciones:
                    self._precalculo_recursivo(decl, nivel + 1, decl.nombre.lower())
            
        elif tipo_nodo in ('declaracion_procedimiento', 'declaracion_funcion'):
            nombre_ambito = nodo.nombre.lower()
            num_parametros = len(nodo.parametros)
            self.info_params[nombre_ambito] = num_parametros
            
            # 1. Asignar offsets a parámetros (negativos)
            for i, param_info in enumerate(nodo.parametros):
                nombre_param = param_info['nombre']
                clave_simbolo = f"{nombre_ambito}.{nombre_param}"
                # Desplazamiento MEPA para parámetros: -(n+3-i)
                offset_param = -(num_parametros + 3 - (i + 1))
                self.info_offsets[clave_simbolo] = offset_param
            
            # 2. Asignar offset para el valor de retorno (si es función)
            if tipo_nodo == 'declaracion_funcion':
                clave_retorno = f"{nombre_ambito}.{nodo.nombre.lower()}"
                # Desplazamiento MEPA para retorno: -(n+3)
                offset_retorno = -(num_parametros + 3)
                self.info_offsets[clave_retorno] = offset_retorno

            # 3. Asignar offsets a variables locales (positivos)
            offset_local = 0
            for clave, simbolo in self.tabla_simbolos.tabla.items():
                # Busca variables locales (ámbito = nombre de la subrutina)
                if simbolo['ambito'] == nombre_ambito and simbolo['categoria'] == 'variable':
                    # Si el símbolo no está ya en offsets (es decir, no es un param), asígnale uno
                    if clave not in self.info_offsets:
                        self.info_offsets[clave] = offset_local
                        offset_local += 1
            self.info_locales[nombre_ambito] = offset_local
            
            # 4. Recorrer declaraciones anidadas
            if nodo.declaraciones_internas:
                for decl_interna in nodo.declaraciones_internas:
                    self._precalculo_recursivo(decl_interna, nivel + 1, decl_interna.nombre.lower())


    # --- Funciones de ayuda para la Generación de Código ---

    def buscar_info_simbolo(self, nombre: str):
        """
        Busca un símbolo en la tabla de símbolos (respetando el ámbito)
        y devuelve su información de nivel y offset calculada.
        """
        # 1. Buscar en la tabla de símbolos original
        simbolo_ts = self.tabla_simbolos.buscar(nombre, self.ambito_actual_gen)
        if not simbolo_ts:
            # Si no se encuentra en el ámbito actual, intentar buscar globalmente
            simbolo_ts = self.tabla_simbolos.buscar(nombre, "global")
            if not simbolo_ts:
                raise Exception(f"Error interno del generador: Símbolo '{nombre}' no encontrado en la tabla de símbolos.")

        # 2. Construir la clave única que usamos en el pre-cálculo
        ambito_simbolo = simbolo_ts['ambito']
        clave_unica = f"{ambito_simbolo}.{simbolo_ts['nombre']}" if ambito_simbolo != "global" else simbolo_ts['nombre']
        
        # 3. Para funciones/procedimientos, no necesitan offset
        if simbolo_ts['categoria'] in ('funcion', 'procedimiento'):
            # Si estamos en el contexto de una asignación a una función, 
            # necesitamos el offset del slot de retorno
            if self.ambito_actual_gen == simbolo_ts['nombre'] and simbolo_ts['categoria'] == 'funcion':
                # Estamos asignando al nombre de la función dentro de su propio cuerpo
                nombre_ambito = simbolo_ts['nombre']
                num_params = self.info_params.get(nombre_ambito, 0)
                offset_retorno = -(num_params + 3)
                nivel = self.info_niveles[nombre_ambito]
                return {'nivel': nivel, 'offset': offset_retorno, 'tipo': simbolo_ts['tipo'], 'categoria': simbolo_ts['categoria'], 'nombre': simbolo_ts['nombre']}
            else:
                # Uso normal de función/procedimiento (llamada)
                return {'nivel': None, 'offset': None, 'tipo': simbolo_ts['tipo'], 'categoria': simbolo_ts['categoria'], 'nombre': simbolo_ts['nombre']}
        
        # 4. Verificar que el símbolo tiene offset asignado
        if clave_unica not in self.info_offsets:
            # Si es una variable global, intentar usar la clave simple
            if ambito_simbolo == "global" and simbolo_ts['nombre'] in self.info_offsets:
                clave_unica = simbolo_ts['nombre']
            else:
                raise Exception(f"Error interno del generador: Símbolo '{nombre}' (clave: {clave_unica}) no tiene offset asignado.")
                
        # 5. Obtener info de nivel y offset
        if ambito_simbolo not in self.info_niveles:
            raise Exception(f"Error interno del generador: Ámbito '{ambito_simbolo}' no tiene nivel asignado.")
            
        nivel = self.info_niveles[ambito_simbolo]
        offset = self.info_offsets[clave_unica]
        
        return {'nivel': nivel, 'offset': offset, 'tipo': simbolo_ts['tipo'], 'categoria': simbolo_ts['categoria']}



    # --- PASO 2: GENERACIÓN DE CÓDIGO MEPA ---

    def generar(self, nodo_raiz: NodoPrograma):
        """
        Punto de entrada principal para generar código.
        """
        # PASO 1: Calcular niveles y offsets
        self.precalculo(nodo_raiz)
        
        # PASO 2: Generar el código MEPA
        self._generar_recursivo(nodo_raiz)


    def _generar_recursivo(self, nodo):
        """
        Punto de entrada recursivo para generar código desde un nodo AST.
        """
        if not nodo:
            return

        metodo_generador = f"generar_{nodo.tipo_nodo}"
        if hasattr(self, metodo_generador):
            # Llama al método específico (ej: generar_asignacion(nodo))
            getattr(self, metodo_generador)(nodo)
        else:
            raise ValueError(f"No hay generador MEPA para el tipo de nodo: {nodo.tipo_nodo}")

    # --- Generadores de Sentencias (S) ---

    def generar_programa(self, nodo_programa):
        """Genera el wrapper del programa principal."""
        
        # Prólogo del programa principal
        self.emitir('INPP') # Inicializar máquina 
        num_globales = self.info_locales.get('global', 0)
        if num_globales > 0:
            self.emitir('RMEM', num_globales) # Reservar memoria para globales 
        
        # Saltar sobre las definiciones de subrutinas
        etiqueta_main = self.nueva_etiqueta()
        self.emitir('DSVS', etiqueta_main) # Desviar siempre a main 
        
        # Generar código para las subrutinas declaradas
        if nodo_programa.declaraciones:
            for decl in nodo_programa.declaraciones:
                self._generar_recursivo(decl)
                
        # --- Comienzo del bloque principal ---
        self.emitir_etiqueta(etiqueta_main)
        
        # Estado de generación para el bloque principal
        self.ambito_actual_gen = "global"
        self.nivel_actual_gen = 0
        
        # Generar código del bloque principal
        self._generar_recursivo(nodo_programa.bloque)
        
        # Epílogo del programa principal
        if num_globales > 0:
            self.emitir('LMEM', num_globales) # Liberar memoria de globales 
        self.emitir('PARA') # Parar la máquina 

    def generar_declaracion_procedimiento(self, nodo_decl):
        """Genera el código para una definición de procedimiento."""
        
        # Guardar estado anterior
        ambito_anterior = self.ambito_actual_gen
        nivel_anterior = self.nivel_actual_gen
        
        # Establecer nuevo estado
        self.ambito_actual_gen = nodo_decl.nombre.lower()
        self.nivel_actual_gen = self.info_niveles[self.ambito_actual_gen]
        
        etiqueta_proc = self.ambito_actual_gen
        num_locales = self.info_locales.get(self.ambito_actual_gen, 0)
        num_params = self.info_params.get(self.ambito_actual_gen, 0)
        
        # --- Prólogo del Procedimiento ---
        self.emitir_etiqueta(etiqueta_proc)
        self.emitir('ENPR', self.nivel_actual_gen) # Entrar a procedimiento 
        if num_locales > 0:
            self.emitir('RMEM', num_locales) # Reservar memoria local 
            
        # Generar código para declaraciones anidadas
        if nodo_decl.declaraciones_internas:
            for decl in nodo_decl.declaraciones_internas:
                self._generar_recursivo(decl)
                
        # Generar código para el cuerpo
        self._generar_recursivo(nodo_decl.bloque_cuerpo)
        
        # --- Epílogo del Procedimiento ---
        if num_locales > 0:
            self.emitir('LMEM', num_locales) # Liberar memoria local 
        self.emitir('RTPR', self.nivel_actual_gen, num_params) # Retornar de procedimiento 
        
        # Restaurar estado anterior
        self.ambito_actual_gen = ambito_anterior
        self.nivel_actual_gen = nivel_anterior

    def generar_declaracion_funcion(self, nodo_decl):
        """Genera el código para una definición de función."""
        
        # Guardar estado anterior
        ambito_anterior = self.ambito_actual_gen
        nivel_anterior = self.nivel_actual_gen
        
        # Establecer nuevo estado
        self.ambito_actual_gen = nodo_decl.nombre.lower()
        self.nivel_actual_gen = self.info_niveles[self.ambito_actual_gen]
        
        etiqueta_func = self.ambito_actual_gen
        num_locales = self.info_locales.get(self.ambito_actual_gen, 0)
        num_params = self.info_params.get(self.ambito_actual_gen, 0)
        
        # --- Prólogo de la Función ---
        self.emitir_etiqueta(etiqueta_func)
        self.emitir('ENPR', self.nivel_actual_gen) # Entrar a procedimiento (función) 
        if num_locales > 0:
            self.emitir('RMEM', num_locales) # Reservar memoria local 
            
        # Generar código para declaraciones anidadas
        if nodo_decl.declaraciones_internas:
            for decl in nodo_decl.declaraciones_internas:
                self._generar_recursivo(decl)
                
        # Generar código para el cuerpo
        self._generar_recursivo(nodo_decl.bloque_cuerpo)
        
        # --- Epílogo de la Función ---
        # El valor de retorno ya está en la pila, en el espacio reservado por el llamador
        if num_locales > 0:
            self.emitir('LMEM', num_locales) # Liberar memoria local 
        self.emitir('RTPR', self.nivel_actual_gen, num_params) # Retornar (igual que proc) 
        
        # Restaurar estado anterior
        self.ambito_actual_gen = ambito_anterior
        self.nivel_actual_gen = nivel_anterior

    def generar_bloque(self, nodo_bloque):
        """Genera código para una secuencia de sentencias."""
        for sentencia in nodo_bloque.sentencias:
            self._generar_recursivo(sentencia)

    def generar_asignacion(self, nodo_asignacion):
        """Genera código para S -> id := E"""
        
        # 1. Generar código para la expresión E.
        self._generar_recursivo(nodo_asignacion.expresion)
        
        # 2. Obtener la información del símbolo
        nombre_var = nodo_asignacion.variable.nombre
        info_var = self.buscar_info_simbolo(nombre_var)
        
        # 3. Handle function return assignment specially
        if info_var['categoria'] == 'funcion':
            # For function return assignment, use the special return slot offset
            nombre_ambito = info_var['nombre']  # Function name is the ambit
            num_params = self.info_params.get(nombre_ambito, 0)
            offset_retorno = -(num_params + 3)
            nivel = self.info_niveles[nombre_ambito]
            self.emitir('ALVL', nivel, offset_retorno)
        else:
            # Regular variable assignment
            self.emitir('ALVL', info_var['nivel'], info_var['offset'])

    def generar_if(self, nodo_if):
        """Genera código para if E then S1 [else S2]"""
        
        # 1. Generar código para la condición E
        self._generar_recursivo(nodo_if.condicion)
        # La pila ahora contiene 0 (false) o 1 (true)
        
        etiqueta_false = self.nueva_etiqueta()
        
        # 2. Emitir salto condicional si es falso
        self.emitir('DSVF', etiqueta_false) # Desviar si es falso 
        
        # 3. Código del 'then' (S1.code)
        self._generar_recursivo(nodo_if.cuerpo_true)

        if nodo_if.cuerpo_false:
            # 4. Si hay 'else', saltar al final
            etiqueta_fin = self.nueva_etiqueta()
            self.emitir('DSVS', etiqueta_fin) # Desviar siempre 
            
            # 5. Etiqueta para el 'false'
            self.emitir_etiqueta(etiqueta_false)
            
            # 6. Código del 'else' (S2.code)
            self._generar_recursivo(nodo_if.cuerpo_false)
            
            # 7. Etiqueta final
            self.emitir_etiqueta(etiqueta_fin)
        else:
            # 3. Si no hay 'else', la etiqueta 'false' es el final
            self.emitir_etiqueta(etiqueta_false)

    def generar_while(self, nodo_while):
        """Genera código para while E do S"""
        etiqueta_inicio = self.nueva_etiqueta()
        etiqueta_fin = self.nueva_etiqueta()
        
        # 1. Etiqueta de inicio del bucle
        self.emitir_etiqueta(etiqueta_inicio)
        
        # 2. Código de la condición E
        self._generar_recursivo(nodo_while.condicion)
        # La pila contiene 0 (false) o 1 (true)
        
        # 3. Salir del bucle si es falso
        self.emitir('DSVF', etiqueta_fin) # 
        
        # 4. Código del cuerpo (S.code)
        self._generar_recursivo(nodo_while.cuerpo)
        
        # 5. Volver al inicio
        self.emitir('DSVS', etiqueta_inicio) # 
        
        # 6. Etiqueta de salida del bucle
        self.emitir_etiqueta(etiqueta_fin)

    def generar_llamada_procedimiento(self, nodo_call):
        """Genera código para call id(Elist)"""
        
        # 1. Evaluar parámetros y apilarlos
        if nodo_call.parametros:
            for param in nodo_call.parametros:
                self._generar_recursivo(param)
        
        # 2. Emitir la llamada
        etiqueta_proc = nodo_call.nombre.lower()
        self.emitir('LLPR', etiqueta_proc) # Llamar a procedimiento 

    def generar_read(self, nodo_read):
        """Genera código para read(id)"""
        # 1. Leer valor de entrada y apilarlo
        self.emitir('LEER') # 
        
        # 2. Almacenar el valor apilado en la variable
        nombre_var = nodo_read.variable.nombre
        info_var = self.buscar_info_simbolo(nombre_var)
        self.emitir('ALVL', info_var['nivel'], info_var['offset']) # 
    
    def generar_write(self, nodo_write):
        """Genera código para write(E)"""
        # 1. Evaluar la expresión E y apilar su valor
        self._generar_recursivo(nodo_write.expresion)
        
        # 2. Imprimir el valor del tope de la pila
        self.emitir('IMPR') # 
    
    # --- Generadores de Expresiones (E) ---
    
    def generar_expresion(self, nodo_expresion):
        """Wrapper para expresiones entre paréntesis."""
        self._generar_recursivo(nodo_expresion.expresion)

    def generar_identificador(self, nodo_id):
        """Genera código para E -> id"""
        # 1. Obtener la dirección (nivel, offset)
        info_var = self.buscar_info_simbolo(nodo_id.nombre)
        
        # 2. Emitir APVL (Apilar Valor)
        self.emitir('APVL', info_var['nivel'], info_var['offset']) # 

    def generar_numero(self, nodo_num):
        """Genera código para E -> numero"""
        self.emitir('APCT', nodo_num.valor) # Apilar constante 
        
    def generar_booleano(self, nodo_bool):
        """Genera código para E -> true | false"""
        # MEPA representa true=1 y false=0 
        valor = 1 if nodo_bool.valor == 'true' else 0
        self.emitir('APCT', valor) # 

    def generar_operacion_binaria(self, nodo_op):
        """Genera código para E -> E1 op E2"""
        
        # 1. Generar código para E1 (deja valor en la pila)
        self._generar_recursivo(nodo_op.izquierda)
        
        # 2. Generar código para E2 (deja valor en la pila)
        self._generar_recursivo(nodo_op.derecha)
        
        # Pila ahora: ..., valor(E1), valor(E2)
        
        # 3. Emitir la instrucción MEPA correspondiente
        op = nodo_op.operador
        if op == '+':
            self.emitir('SUMA') # 
        elif op == '-':
            self.emitir('SUST') # 
        elif op == '*':
            self.emitir('MULT') # 
        elif op == 'div':
            self.emitir('DIVI') # 
        elif op == 'or':
            self.emitir('DISJ') # Disyunción 
        elif op == 'and':
            self.emitir('CONJ') # Conjunción 
        elif op == '=':
            self.emitir('CMIG') # Comparar igual 
        elif op == '<>':
            self.emitir('CMDG') # Comparar desigual 
        elif op == '<':
            self.emitir('CMME') # Comparar menor 
        elif op == '>':
            self.emitir('CMMA') # Comparar mayor 
        elif op == '<=':
            self.emitir('CMNI') # Comparar menor o igual 
        elif op == '>=':
            self.emitir('CMYI') # Comparar mayor o igual 
        else:
            raise ValueError(f"Operador binario MEPA no reconocido: {op}")
        
        # La instrucción MEPA consume los dos valores y apila el resultado

    def generar_operacion_unaria(self, nodo_op):
        """Genera código para E -> op E1"""
        
        # 1. Generar código para E1 (deja valor en la pila)
        self._generar_recursivo(nodo_op.operando)
        
        # Pila ahora: ..., valor(E1)
        
        # 2. Emitir la instrucción MEPA
        op = nodo_op.operador
        if op == '-':
            self.emitir('UMEN') # Menos unario 
        elif op == 'not':
            self.emitir('NEGA') # Negación lógica 
        else:
            raise ValueError(f"Operador unario MEPA no reconocido: {op}")
            
        # La instrucción consume el valor y apila el resultado

    def generar_llamada_funcion(self, nodo_call):
        """Genera código para E -> id(Elist)"""
        
        # 1. Reservar espacio en la pila para el valor de retorno
        self.emitir('RMEM', 1) # 
        
        # 2. Evaluar parámetros y apilarlos
        if nodo_call.parametros:
            for param in nodo_call.parametros:
                self._generar_recursivo(param)
        
        # 3. Emitir la llamada
        etiqueta_func = nodo_call.nombre.lower()
        self.emitir('LLPR', etiqueta_func) # 
        
        # Al regresar, el valor de retorno está en el tope de la pila