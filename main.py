import sys
import os
from lexico import AnalizadorLexico
from sintactico import sintactico
from generador_mepa import GeneradorMEPA

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 main.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    analizador = AnalizadorLexico()
    analizador.cargar_archivo(input_file)

    try:
        # Análisis sintáctico y semántico (construye AST)
        ast = sintactico(analizador)
        
        # Obtener la tabla de símbolos del analizador semántico
        from sintactico import semantico
        tabla_simbolos = semantico.tabla_simbolos
        
        # Generar código intermedio
        generador = GeneradorMEPA(tabla_simbolos)
        generador.generar(ast)
        
        # Mostrar código intermedio generado
        codigo = generador.obtener_codigo()
        output_file = os.path.splitext(input_file)[0] + ".mepa"
        with open(output_file, "w") as f:
            f.write(codigo)

        print(f"MEPA code saved to: {output_file}")

    except SyntaxError as e:
        print(e)
