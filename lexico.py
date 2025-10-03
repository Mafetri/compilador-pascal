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
    'read': 'read',
    'write': 'write',
    'or': ('oper_logico', 'or'),
    'and': ('oper_logico', 'and'),
    'not': ('oper_logico', 'not'),
    'true': 'true',
    'false': 'false'
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

    def next_token(self):
        """Genera y devuelve el siguiente token junto con su valor y posición (tipo, valor, línea, columna)"""
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
                    self.advance()
                    return ('punto_coma', ';', start_line, start_col)
                elif input_char == ',':
                    self.advance()
                    return ('coma', ',', start_line, start_col)
                elif input_char == '.':
                    self.advance()
                    return ('punto', '.', start_line, start_col)
                elif input_char == '(':
                    self.advance()
                    return ('parentesis_izq', '(', start_line, start_col)
                elif input_char == ')':
                    self.advance()
                    return ('parentesis_der', ')', start_line, start_col)
                elif input_char == '+':
                    self.advance()
                    return ('+', '+', start_line, start_col)
                elif input_char == '-':
                    self.advance()
                    return ('-', '-', start_line, start_col)
                elif input_char == '*':
                    self.advance()
                    return ('*', '*', start_line, start_col)
                elif input_char == '/':
                    self.advance()
                    return ('div', '/', start_line, start_col)
                elif input_char == '=':
                    self.advance()
                    return ('=', '=', start_line, start_col)
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
                    raise SyntaxError(f"Lexical error at line {start_line}, column {start_col}: invalid character '{input_char}'")

            # Estado: saw_colon
            elif self.state == "saw_colon":
                if input_char == '=':
                    self.advance()
                    self.state = "start"
                    return ('asignacion', ':=', start_line, start_col)
                else:
                    self.state = "start"
                    return ('asignacion_de_tipo', ':', start_line, start_col)

            # Estado: in_comment
            elif self.state == "in_comment":
                if input_char == '}':
                    self.state = "start"
                self.advance()
                continue

            # Estado: saw_less_than
            elif self.state == "saw_less_than":
                if input_char == '=':
                    self.advance()
                    self.state = "start"
                    return ('<=', '<=', start_line, start_col)
                elif input_char == '>':
                    self.advance()
                    self.state = "start"
                    return ('<>', '<>', start_line, start_col)
                else:
                    self.state = "start"
                    return ('<', '<', start_line, start_col)

            # Estado: saw_greater_than
            elif self.state == "saw_greater_than":
                if input_char == '=':
                    self.advance()
                    self.state = "start"
                    return ('>=', '>=', start_line, start_col)
                else:
                    self.state = "start"
                    return ('>', '>', start_line, start_col)

            # Estado: in_identificador
            elif self.state == "in_identificador":
                if self.is_letter(input_char) or self.is_digit(input_char):
                    self.current_token += input_char
                    self.advance()
                else:
                    self.state = "start"
                    token_value = self.current_token
                    if token_value in palabras_reservadas:
                        token_info = palabras_reservadas[token_value]
                        if isinstance(token_info, tuple):
                            return (token_info[1], token_value, start_line, start_col)  # e.g., 'or', 'and', 'not'
                        return (token_info, token_value, start_line, start_col)  # e.g., 'program', 'var'
                    return ('ident', token_value, start_line, start_col)

            # Estado: in_natural
            elif self.state == "in_natural":
                if self.is_digit(input_char):
                    self.current_token += input_char
                    self.advance()
                else:
                    self.state = "start"
                    token_value = self.current_token
                    return ('numero', token_value, start_line, start_col)

        # Handle final states when input is exhausted
        if self.state == "in_identificador":
            self.state = "start"
            token_value = self.current_token
            if token_value in palabras_reservadas:
                token_info = palabras_reservadas[token_value]
                if isinstance(token_info, tuple):
                    return (token_info[1], token_value, self.linea, self.columna)
                return (token_info, token_value, self.linea, self.columna)
            return ('ident', token_value, self.linea, self.columna)
        elif self.state == "in_natural":
            self.state = "start"
            token_value = self.current_token
            return ('numero', token_value, self.linea, self.columna)
        elif self.state == "saw_colon":
            self.state = "start"
            return ('asignacion_de_tipo', ':', self.linea, self.columna)
        elif self.state == "saw_less_than":
            self.state = "start"
            return ('<', '<', self.linea, self.columna)
        elif self.state == "saw_greater_than":
            self.state = "start"
            return ('>', '>', self.linea, self.columna)
        return (None, None, self.linea, self.columna)  # End of input