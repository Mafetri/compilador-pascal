from lexico import AnalizadorLexico
from sintactico import sintactico
import glob
import os

error_map = {}
error_file = "./pascal_test/errores.txt"
try:
    with open(error_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                file_name, error_desc = line.split(": ", 1)
                error_map[file_name] = error_desc
except FileNotFoundError:
    print(f"Error: {error_file} not found.")
    exit(1)
except Exception as e:
    print(f"Error reading {error_file}: {e}")
    exit(1)

pas_files = glob.glob("./pascal_test/*.pas")

for file_path in pas_files:
    file_name = os.path.basename(file_path)
    print(f'\n{file_path}')
    
    print('Lexico:', end=' ')
    try:
        analizador = AnalizadorLexico()
        analizador.cargar_archivo(file_path)
        analizador.analizar()
        tokens = analizador.obtener_lista_para_parser()
        print('Ok')
    except Exception as e:
        print(f"Caught exception during lexical analysis: {e}")
        break

    print('Sintactico:', end=' ')
    try:
        sintactico(tokens)
        print('Ok')
    except SyntaxError as e:
        print(f"Caught syntax error: {e}")
        error_desc = error_map.get(file_name, "Unknown error")
        print(f"Error Real: {error_desc}")