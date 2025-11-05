import pandas as pd
import re
import random

def limpiar_salarios_y_jornada():
    """
    Limpia la columna 'salario' extrayendo solo números y convierte 'jornada' a minúsculas
    """
    print("🧹 LIMPIANDO COLUMNA SALARIO Y JORNADA")
    print("="*50)

    # Leer el CSV
    try:
        df = pd.read_csv('opcionEmpleo_jobs_con_habilidades.csv')
        print(f"✅ Archivo leído exitosamente: {len(df)} registros")
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'opcionEmpleo_jobs_con_habilidades.csv'")
        return

    print("\n🔍 ANALIZANDO SALARIOS ORIGINALES:")
    salarios_unicos = df['salario'].value_counts(dropna=False)
    for i, (salario, count) in enumerate(salarios_unicos.head(10).items()):
        if pd.isna(salario) or salario == '':
            print(f"   VACÍO: {count} registros")
        else:
            print(f"   '{salario}': {count} registros")

    def extraer_numero_salario(salario_text):
        """
        Extrae números del texto de salario y maneja rangos
        """
        if pd.isna(salario_text) or salario_text == '':
            return ''

        salario_str = str(salario_text).lower()

        # Buscar patrones de rangos como "de 300 a 700", "300-700", "300 a 700"
        rango_pattern = r'(\d+)\s*(?:a|hasta|-)\s*(\d+)'
        rango_match = re.search(rango_pattern, salario_str)

        if rango_match:
            min_val = int(rango_match.group(1))
            max_val = int(rango_match.group(2))
            # Tomar un valor aleatorio en el rango
            return str(random.randint(min_val, max_val))

        # Buscar cualquier número en el texto
        numeros = re.findall(r'\d+', salario_str)

        if numeros:
            # Si hay múltiples números, tomar el más grande (generalmente el salario)
            numero_mayor = max([int(num) for num in numeros])
            return str(numero_mayor)

        return ''

    # CAMBIO 1: Limpiar columna salario
    print(f"\n🧹 PROCESANDO SALARIOS...")

    # Aplicar la función de limpieza
    df['salario_limpio'] = df['salario'].apply(extraer_numero_salario)

    # Reemplazar la columna original
    df['salario'] = df['salario_limpio']
    df = df.drop(columns=['salario_limpio'])

    # CAMBIO 2: Convertir jornada a minúsculas
    print(f"🔤 CONVIRTIENDO JORNADA A MINÚSCULAS...")

    def convertir_jornada_minuscula(jornada):
        if pd.isna(jornada) or jornada == '':
            return jornada
        return str(jornada).lower()

    df['jornada'] = df['jornada'].apply(convertir_jornada_minuscula)

    # Mostrar resultados
    print(f"\n✅ RESULTADOS DE LA LIMPIEZA:")

    # Analizar salarios después de limpieza
    salarios_con_valor = df[df['salario'] != '']
    salarios_vacios = df[df['salario'] == '']

    print(f"\n📊 SALARIOS DESPUÉS DE LIMPIEZA:")
    print(f"   Con valor numérico: {len(salarios_con_valor)} registros")
    print(f"   Vacíos: {len(salarios_vacios)} registros")

    if len(salarios_con_valor) > 0:
        print(f"\n📈 ESTADÍSTICAS DE SALARIOS:")
        salarios_numericos = [int(s) for s in salarios_con_valor['salario'] if s.isdigit()]
        if salarios_numericos:
            print(f"   Salario mínimo: ${min(salarios_numericos)}")
            print(f"   Salario máximo: ${max(salarios_numericos)}")
            print(f"   Salario promedio: ${sum(salarios_numericos)//len(salarios_numericos)}")

    # Analizar jornada después de conversión
    print(f"\n📊 JORNADA DESPUÉS DE CONVERSIÓN:")
    jornada_counts = df['jornada'].value_counts(dropna=False)
    for jornada, count in jornada_counts.items():
        if pd.isna(jornada) or jornada == '':
            print(f"   VACÍO: {count} registros")
        else:
            print(f"   '{jornada}': {count} registros")

    # Guardar archivo modificado
    output_filename = 'opcionEmpleo_jobs_con_habilidades_limpio.csv'
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"\n✅ Archivo guardado: {output_filename}")

    # Mostrar ejemplos de cambios
    print(f"\n📋 EJEMPLOS DE CAMBIOS:")
    ejemplos = df.head(5)[['titulo', 'salario', 'jornada']]
    print(ejemplos.to_string(index=False))

    return df

if __name__ == "__main__":
    resultado = limpiar_salarios_y_jornada()

    print("\n" + "="*50)
    print("✅ LIMPIEZA COMPLETADA")
    print("="*50)