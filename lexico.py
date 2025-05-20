# Tabla de palabras reservadas y operadores
palabras_reservadas = {
    'program': 'program',
    'var': 'var',
    'procedure': 'procedure',
    'function': 'function',
    'integer': 'integer',
    'boolean': 'boolean',
    'begin': 'begin',
    'end': 'end',
    'if': 'if',
    'then': 'then',
    'else': 'else',
    'while': 'while',
    'do': 'do',
    'or': ('oper_logico', 'or'),
    'and': ('oper_logico', 'and'),
    'not': ('oper_logico', 'not')
}

simbolos = {
    ':': 'asignacion_de_tipo',
    ':=': 'asignacion',
    ';': 'punto_coma',
    ',': 'coma',
    '.': 'punto',
    '(': 'parentesis_izq',
    ')': 'parentesis_der',
    '+': ('oper_aritmetico', 'suma'),
    '-': ('oper_aritmetico', 'resta'),
    '*': ('oper_aritmetico', 'mult'),
    '/': ('oper_aritmetico', 'div'),
    '=': ('oper_relacional', 'igual'),
    '<': ('oper_relacional', 'menor'),
    '<=': ('oper_relacional', 'menor_igual'),
    '>': ('oper_relacional', 'mayor'),
    '>=': ('oper_relacional', 'mayor_igual'),
    '<>': ('oper_relacional', 'distinto')
}

class AnalizadorLexico:
    def __init__(self):
        self.tokens = []
        self.linea = 1
        self.columna = 1
        self.posicion = 0
        self.texto = ""
        self.current_token = ""
        self.state = "start"

    def cargar_archivo(self, archivo):
        """Lee el contenido del archivo .txt"""
        with open(archivo, 'r') as file:
            self.texto = file.read()

    def is_letter(self, char):
        """Verifica si el carácter es una letra"""
        return char.isalpha()

    def is_digit(self, char):
        """Verifica si el carácter es un dígito"""
        return char.isdigit()

    def is_space(self, char):
        """Verifica si el carácter es un espacio o salto de línea"""
        return char in [' ', '\n', '\t']

    def advance(self):
        """Avanza la posición y actualiza línea/columna"""
        if self.posicion < len(self.texto):
            char = self.texto[self.posicion]
            if char == '\n':
                self.linea += 1
                self.columna = 1
            else:
                self.columna += 1
            self.posicion += 1
            return char
        return None

    def analizar(self):
        """Procesa el texto y genera la lista de tokens"""
        while self.posicion < len(self.texto):
            input_char = self.texto[self.posicion]
            start_line, start_col = self.linea, self.columna

            # Estado inicial: start
            if self.state == "start":
                self.current_token = ""
                if self.is_space(input_char):
                    self.advance()
                    continue
                elif self.is_digit(input_char):
                    self.state = "in_natural"
                    self.current_token += input_char
                    self.advance()
                elif self.is_letter(input_char):
                    self.state = "in_identificador"
                    self.current_token += input_char
                    self.advance()
                elif input_char == ':':
                    self.state = "saw_colon"
                    self.current_token = input_char
                    self.advance()
                elif input_char == ';':
                    self.tokens.append(('punto_coma', ';', start_line, start_col))
                    self.advance()
                    continue
                elif input_char == ',':
                    self.tokens.append(('coma', ',', start_line, start_col))
                    self.advance()
                    continue
                elif input_char == '.':
                    self.tokens.append(('punto', '.', start_line, start_col))
                    self.advance()
                    continue
                elif input_char == '(':
                    self.tokens.append(('parentesis_izq', '(', start_line, start_col))
                    self.advance()
                    continue
                elif input_char == ')':
                    self.tokens.append(('parentesis_der', ')', start_line, start_col))
                    self.advance()
                    continue
                elif input_char == '+':
                    self.tokens.append(('oper_aritmetico', '+', start_line, start_col, 'suma'))
                    self.advance()
                    continue
                elif input_char == '-':
                    self.tokens.append(('oper_aritmetico', '-', start_line, start_col, 'resta'))
                    self.advance()
                    continue
                elif input_char == '*':
                    self.tokens.append(('oper_aritmetico', '*', start_line, start_col, 'mult'))
                    self.advance()
                    continue
                elif input_char == '/':
                    self.tokens.append(('oper_aritmetico', '/', start_line, start_col, 'div'))
                    self.advance()
                    continue
                elif input_char == '=':
                    self.tokens.append(('oper_relacional', '=', start_line, start_col, 'igual'))
                    self.advance()
                    continue
                elif input_char == '<':
                    self.state = "saw_less_than"
                    self.current_token = input_char
                    self.advance()
                elif input_char == '>':
                    self.state = "saw_greater_than"
                    self.current_token = input_char
                    self.advance()
                elif input_char == '{':
                    self.state = "in_comment"
                    self.advance()
                else:
                    self.tokens.append(('ERROR', input_char, start_line, start_col))
                    self.advance()
                    continue

            # Estado: saw_colon (procesa asignaciones de tipos y asignaciones)
            elif self.state == "saw_colon":
                if input_char == '=':
                    self.tokens.append(('asignacion', ':=', start_line, start_col))
                    self.advance()
                else:
                    self.tokens.append(('asignacion_de_tipo', ':', start_line, start_col))
                self.state = "start"
                continue

            # Estado: in_comment (procesa comentarios)
            elif self.state == "in_comment":
                if input_char == '}':
                    self.state = "start"
                self.advance()
                continue

            # Estado: saw_less_than (procesa <, <=, <>)
            elif self.state == "saw_less_than":
                if input_char == '=':
                    self.tokens.append(('oper_relacional', '<=', start_line, start_col, 'menor_igual'))
                    self.advance()
                elif input_char == '>':
                    self.tokens.append(('oper_relacional', '<>', start_line, start_col, 'distinto'))
                    self.advance()
                else:
                    self.tokens.append(('oper_relacional', '<', start_line, start_col, 'menor'))
                self.state = "start"
                continue

            # Estado: saw_greater_than (procesa >, >=)
            elif self.state == "saw_greater_than":
                if input_char == '=':
                    self.tokens.append(('oper_relacional', '>=', start_line, start_col, 'mayor_igual'))
                    self.advance()
                else:
                    self.tokens.append(('oper_relacional', '>', start_line, start_col, 'mayor'))
                self.state = "start"
                continue

            # Estado: in_identificador (procesa identificadores y palabras reservadas)
            elif self.state == "in_identificador":
                if self.is_letter(input_char) or self.is_digit(input_char):
                    self.current_token += input_char
                    self.advance()
                else:
                    if self.current_token in palabras_reservadas:
                        token_info = palabras_reservadas[self.current_token]
                        if isinstance(token_info, tuple):
                            self.tokens.append((token_info[0], self.current_token, start_line, start_col, token_info[1]))
                        else:
                            self.tokens.append((token_info, self.current_token, start_line, start_col))
                    else:
                        self.tokens.append(('id', self.current_token, start_line, start_col))
                    self.state = "start"

            # Estado: in_natural (procesa números enteros)
            elif self.state == "in_natural":
                if self.is_digit(input_char):
                    self.current_token += input_char
                    self.advance()
                else:
                    self.tokens.append(('numero', self.current_token, start_line, start_col))
                    self.state = "start"

    def mostrar_tokens(self):
        """Muestra la lista de tokens generados"""
        for token in self.tokens:
            print(f"(lin. {token[2]:03}, col. {token[3]:03})  {token[1]:<15} ->  {token[0]}" + (f", {token[4]}" if len(token) == 5 else ""))
        # for idx, token in enumerate(self.tokens):
        #     print(f"{idx}: {token[1]}")

    def obtener_lista_para_parser(self):
        simplified = []
        for token in self.tokens:
            tipo = token[0]
            if tipo == 'id':
                simplified.append('ident')
            elif tipo == 'numero':
                simplified.append('numero')
            else:
                simplified.append(token[1])  # use the symbol or keyword
        return simplified

# Ejemplo de uso
if __name__ == "__main__":
    analizador = AnalizadorLexico()
    analizador.cargar_archivo("entrada.txt")
    analizador.analizar()
    analizador.mostrar_tokens()