class TablaSimbolos:
    def __init__(self):
        self.tabla = {}
        self.ambito_actual = "global"
        self.ambitos = ["global"]
        
    def insertar(self, nombre, tipo, categoria, column, row, ambito=None, parametros=None):
        if ambito is None:
            ambito = self.ambito_actual

        clave = f"{ambito}.{nombre}" if ambito != "global" else nombre

        if clave in self.tabla:
            raise SyntaxError(f"Semantic error at line {row}, column {column}: '{nombre}' it already declared in '{ambito}' (col {column}, row {row})")
            
        self.tabla[clave] = {
            'nombre': nombre,               # Nombre del símbolo: ej 'x', 'miFuncion'
            'tipo': tipo,                   # Tipo del símbolo (integer, boolean, etc.)
            'categoria': categoria,         # Categoría (variable, funcion, procedimiento)
            'ambito': ambito,               # Ámbito (global, local, etc.)
            'parametros': parametros or []  # Paraámetros si es función o procedimiento: ej p(a: integer) { 'nombre': 'a', 'tipo': 'integer' }
        }
        
    def buscar(self, nombre, ambito=None):
        if ambito is None:
            ambito = self.ambito_actual
            
        # Buscar en el ámbito actual primero
        clave = f"{ambito}.{nombre}"
        if clave in self.tabla:
            return self.tabla[clave]
            
        # Buscar en ámbitos padres
        ambitos_padres = self.ambitos[:self.ambitos.index(ambito) + 1]
        for ambito_padre in reversed(ambitos_padres):
            clave_padre = f"{ambito_padre}.{nombre}" if ambito_padre != "global" else nombre
            if clave_padre in self.tabla:
                return self.tabla[clave_padre]
                
        # Buscar en global como último recurso
        if nombre in self.tabla and self.tabla[nombre]['ambito'] == 'global':
            return self.tabla[nombre]
            
        return None
        
    def entrar_ambito(self, nombre):
        self.ambito_actual = nombre
        self.ambitos.append(nombre)
        
    def salir_ambito(self):
        if len(self.ambitos) > 1:
            self.ambitos.pop()
            self.ambito_actual = self.ambitos[-1]