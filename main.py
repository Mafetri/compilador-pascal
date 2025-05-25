from lexico import AnalizadorLexico
from sintactico import sintactico

# 1. Analizador Lexico
analizador = AnalizadorLexico()
analizador.cargar_archivo("./entrada.txt")

try:
	sintactico(analizador)
	print('Ok')
except SyntaxError as e:
	print(f"Caught syntax error: {e}")