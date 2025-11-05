import pandas as pd
import re
import random

def analizar_y_limpiar_multitrabajos():
    """
    Analiza valores únicos en 'jornada' y limpia la columna 'salario' del CSV de Multitrabajos
    Además convierte los valores de jornada al español
    """
    print("📊 ANÁLISIS Y LIMPIEZA CSV DE MULTITRABAJOS")
    print("="*60)

    # Leer el CSV
    try:
        df = pd.read_csv('multitrabajos_jobs_con_habilidades.csv')
        print(f"✅ Archivo leído exitosamente: {len(df)} registros")
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'multitrabajos_jobs_con_habilidades.csv'")
        return

    # PARTE 1: ANÁLISIS DE JORNADA ORIGINAL
    print(f"\n🔍 ANÁLISIS DE VALORES ÚNICOS EN LA COLUMNA 'JORNADA' (ORIGINAL):")
    print("-" * 60)

    valores_jornada = df['jornada'].value_counts(dropna=False)
    print(f"Total de tipos diferentes: {len(valores_jornada)}")
    print()

    for i, (valor, cantidad) in enumerate(valores_jornada.items(), 1):
        if pd.isna(valor) or valor == '':
            print(f"{i:2d}. VACÍO/NULL: {cantidad:3d} registros ({cantidad/len(df)*100:.1f}%)")
        else:
            print(f"{i:2d}. '{valor}': {cantidad:3d} registros ({cantidad/len(df)*100:.1f}%)")

    # PARTE 2: ANÁLISIS DE SALARIOS ORIGINALES
    print(f"\n🔍 ANÁLISIS DE SALARIOS ORIGINALES:")
    print("-" * 40)

    salarios_unicos = df['salario'].value_counts(dropna=False)
    for i, (salario, count) in enumerate(salarios_unicos.head(10).items()):
        if pd.isna(salario) or salario == '':
            print(f"   VACÍO: {count} registros")
        else:
            print(f"   '{salario}': {count} registros")

    # PARTE 3: FUNCIÓN PARA LIMPIAR SALARIOS
    def extraer_numero_salario(salario_text):
        """
        Extrae números del texto de salario y maneja rangos
        """
        if pd.isna(salario_text) or salario_text == '':
            return ''

        salario_str = str(salario_text).lower()

        # Casos especiales
        if 'salarios' in salario_str:
            return ''

        # Buscar patrones de rangos como "De $1.200 A $1.700", "de 300 a 700", "300-700"
        rango_pattern = r'de?\s*\$?(\d+(?:\.\d+)?)\s*(?:a|hasta|-)\s*\$?(\d+(?:\.\d+)?)'
        rango_match = re.search(rango_pattern, salario_str)

        if rango_match:
            min_val = float(rango_match.group(1).replace('.', ''))
            max_val = float(rango_match.group(2).replace('.', ''))
            # Tomar un valor aleatorio en el rango
            return str(int(random.uniform(min_val, max_val)))

        # Buscar cualquier número en el texto (eliminando puntos como separadores de miles)
        numeros = re.findall(r'\d+(?:\.\d+)?', salario_str)

        if numeros:
            # Convertir números y tomar el más grande
            numeros_convertidos = []
            for num in numeros:
                if '.' in num and len(num.split('.')[1]) <= 2:
                    # Es decimal
                    numeros_convertidos.append(float(num))
                else:
                    # Eliminar punto como separador de miles
                    num_sin_punto = num.replace('.', '')
                    numeros_convertidos.append(float(num_sin_punto))

            numero_mayor = max(numeros_convertidos)
            return str(int(numero_mayor))

        return ''

    # PARTE 4: APLICAR LIMPIEZA DE SALARIOS
    print(f"\n🧹 PROCESANDO SALARIOS...")

    # Aplicar la función de limpieza
    df['salario_limpio'] = df['salario'].apply(extraer_numero_salario)

    # Reemplazar la columna original
    df['salario'] = df['salario_limpio']
    df = df.drop(columns=['salario_limpio'])

    # PARTE 5: CONVERTIR JORNADA AL ESPAÑOL
    print(f"\n🔤 CONVIRTIENDO JORNADA AL ESPAÑOL...")

    def convertir_jornada_espanol(jornada):
        """
        Convierte los valores de jornada del inglés al español
        """
        if pd.isna(jornada) or jornada == '':
            return jornada

        jornada_str = str(jornada)

        # Mapear valores específicos
        if jornada_str == 'Full-time':
            return 'tiempo completo'
        elif jornada_str == 'Full-time, Indeterminado':
            return 'tiempo completo indeterminado'
        elif jornada_str == 'Full-time, Temporal':
            return 'tiempo completo temporal'
        else:
            # Si hay algún valor no esperado, mantenerlo
            return jornada_str

    # Aplicar la conversión
    df['jornada'] = df['jornada'].apply(convertir_jornada_espanol)

    # PARTE 6: MOSTRAR RESULTADOS
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
    print(f"\n🔍 VALORES DE JORNADA DESPUÉS DE CONVERSIÓN AL ESPAÑOL:")
    print("-" * 60)
    valores_jornada_nuevos = df['jornada'].value_counts(dropna=False)
    for i, (valor, cantidad) in enumerate(valores_jornada_nuevos.items(), 1):
        if pd.isna(valor) or valor == '':
            print(f"{i:2d}. VACÍO/NULL: {cantidad:3d} registros ({cantidad/len(df)*100:.1f}%)")
        else:
            print(f"{i:2d}. '{valor}': {cantidad:3d} registros ({cantidad/len(df)*100:.1f}%)")

    # Guardar archivo modificado
    output_filename = 'multitrabajos_jobs_con_habilidades_limpio.csv'
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"\n✅ Archivo guardado: {output_filename}")

    # Mostrar ejemplos finales
    print(f"\n📋 MUESTRA DEL ARCHIVO FINAL:")
    ejemplos = df.head(3)[['titulo', 'salario', 'jornada']]
    print(ejemplos.to_string(index=False))

    return df

if __name__ == "__main__":
    resultado = analizar_y_limpiar_multitrabajos()

    print("\n" + "="*60)
    print("✅ ANÁLISIS Y LIMPIEZA COMPLETADOS")
    print("="*60)