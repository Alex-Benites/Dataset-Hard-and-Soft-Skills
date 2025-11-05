import pandas as pd
import numpy as np

def modificar_bing_csv():
    """
    Modifica el CSV de Bing agregando las columnas 'salario' y 'jornada',
    y reordena las columnas según el orden especificado
    """
    print("🔧 MODIFICANDO CSV DE BING")
    print("="*50)

    # Leer el CSV
    try:
        df = pd.read_csv('bing_jobs_con_habilidades.csv')
        print(f"✅ Archivo leído exitosamente: {len(df)} registros")
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'bing_jobs_con_habilidades.csv'")
        return

    print("\nColumnas originales:", df.columns.tolist())

    # CAMBIO 1: Agregar la columna 'salario' con valores vacíos
    df['salario'] = ''
    print("✅ Columna 'salario' agregada (valores vacíos)")

    # CAMBIO 2: Agregar la columna 'jornada'
    # Llenar la mayoría con "tiempo completo" y algunos con valores vacíos
    np.random.seed(42)  # Para reproducibilidad
    total_registros = len(df)

    # 80% será "tiempo completo", 20% valores vacíos
    jornada_values = ['tiempo completo'] * int(total_registros * 0.8) + [''] * (total_registros - int(total_registros * 0.8))

    # Mezclar aleatoriamente
    np.random.shuffle(jornada_values)
    df['jornada'] = jornada_values

    tiempo_completo_count = (df['jornada'] == 'tiempo completo').sum()
    vacios_count = (df['jornada'] == '').sum()

    print(f"✅ Columna 'jornada' agregada:")
    print(f"   - 'tiempo completo': {tiempo_completo_count} registros")
    print(f"   - Vacíos: {vacios_count} registros")

    # CAMBIO 3: Reordenar las columnas según el orden especificado
    orden_columnas = [
        'titulo',
        'empresa',
        'ubicacion',
        'salario',      # Nueva columna
        'modalidad',
        'jornada',      # Nueva columna
        'Area',
        'habilidades_hard',
        'habilidades_soft'
    ]

    # Verificar que todas las columnas existan
    columnas_existentes = []
    for col in orden_columnas:
        if col in df.columns:
            columnas_existentes.append(col)
        else:
            print(f"⚠️  Columna '{col}' no encontrada")

    # Reordenar DataFrame
    df = df[columnas_existentes]
    print("✅ Columnas reordenadas según el orden especificado")

    print("\nColumnas finales:", df.columns.tolist())

    # Guardar el archivo modificado
    output_filename = 'bing_jobs_con_habilidades_modificado.csv'
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"\n✅ Archivo guardado exitosamente: {output_filename}")
    print(f"📊 Total de registros: {len(df)}")
    print(f"📋 Columnas finales: {len(df.columns)}")

    # Mostrar muestra de los cambios
    print("\n📋 MUESTRA DE LOS CAMBIOS:")
    print("Primeras 3 filas con el nuevo orden:")
    muestra_columnas = ['titulo', 'salario', 'modalidad', 'jornada', 'Area']
    print(df.head(3)[muestra_columnas].to_string())

    # Verificar que los cambios se realizaron correctamente
    print(f"\n🔍 VERIFICACIÓN:")
    print(f"   ✅ Columna 'salario' agregada: {'salario' in df.columns}")
    print(f"   ✅ Columna 'jornada' agregada: {'jornada' in df.columns}")
    print(f"   ✅ Orden correcto de columnas: {df.columns.tolist() == orden_columnas}")

    # Estadísticas de jornada
    print(f"\n📊 ESTADÍSTICAS DE JORNADA:")
    jornada_stats = df['jornada'].value_counts(dropna=False)
    for valor, count in jornada_stats.items():
        if pd.isna(valor) or valor == '':
            print(f"   Vacíos: {count} registros")
        else:
            print(f"   '{valor}': {count} registros")

    # Verificar que todos los salarios están vacíos
    salarios_vacios = (df['salario'] == '').sum()
    print(f"\n📊 ESTADÍSTICAS DE SALARIO:")
    print(f"   Registros con salario vacío: {salarios_vacios}/{len(df)}")

    return df

if __name__ == "__main__":
    df_resultado = modificar_bing_csv()

    print("\n" + "="*50)
    print("✅ MODIFICACIONES COMPLETADAS")
    print("="*50)