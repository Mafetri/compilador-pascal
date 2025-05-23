from lexico import AnalizadorLexico
from sintactico import sintactico

# 1. Analizador Lexico
print('Analizador Lexico: \n')
analizador = AnalizadorLexico()
analizador.cargar_archivo("./entrada.txt")
analizador.analizar()
analizador.mostrar_tokens()
tokens = analizador.obtener_lista_para_parser()

# 2. Analizador Sintactico
print('Analizador Lexico: \n')
sintactico(tokens)

print("Análisis sintáctico completado sin errores.")
