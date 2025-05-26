import sys
from lexico import AnalizadorLexico
from sintactico import sintactico

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 main.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    analizador = AnalizadorLexico()
    analizador.cargar_archivo(input_file)

    try:
        sintactico(analizador)
        print('Ok')
    except SyntaxError as e:
        print(f"Caught syntax error: {e}")
