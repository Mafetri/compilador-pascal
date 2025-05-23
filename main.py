from lexico import AnalizadorLexico
from sintactico import sintactico

# 1. Analizador Lexico
print('Analizador Lexico: \n')
analizador = AnalizadorLexico()
analizador.cargar_archivo("./pascal_test/Ej16a.pas")
analizador.analizar()
analizador.mostrar_tokens()
tokens = analizador.obtener_lista_para_parser()

# 2. Analizador Sintactico
# print('Analizador Lexico: \n')
# sintactico(tokens)

try:
	sintactico(tokens)
	print('Ok')
except SyntaxError as e:
	print(f"Caught syntax error: {e}")