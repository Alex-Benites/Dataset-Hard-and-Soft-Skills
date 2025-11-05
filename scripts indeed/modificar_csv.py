import pandas as pd
import numpy as np

def modificar_indeed_csv():
    """
    Modifica el CSV de Indeed agregando la columna 'jornada',
    y reordena las columnas según el orden especificado
    """
    print("🔧 MODIFICANDO CSV DE INDEED")
    print("="*50)

    # Leer el CSV
    try:
        df = pd.read_csv('indeed_jobs_con_habilidades.csv')
        print(f"✅ Archivo leído exitosamente: {len(df)} registros")
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'indeed_jobs_con_habilidades.csv'")
        return

    print("\nColumnas originales:", df.columns.tolist())

    # CAMBIO 1: Agregar la columna 'jornada'
    # 50% será "tiempo completo", 50% valores vacíos
    np.random.seed(42)  # Para reproducibilidad
    total_registros = len(df)

    # 50% será "tiempo completo", 50% valores vacíos
    jornada_values = ['tiempo completo'] * int(total_registros * 0.5) + [''] * (total_registros - int(total_registros * 0.5))

    # Mezclar aleatoriamente
    np.random.shuffle(jornada_values)
    df['jornada'] = jornada_values

    tiempo_completo_count = (df['jornada'] == 'tiempo completo').sum()
    vacios_count = (df['jornada'] == '').sum()

    print(f"✅ Columna 'jornada' agregada:")
    print(f"   - 'tiempo completo': {tiempo_completo_count} registros")
    print(f"   - Vacíos: {vacios_count} registros")

    # CAMBIO 2: Reordenar las columnas según el orden especificado
    orden_columnas = [
        'titulo',
        'empresa',
        'ubicacion',
        'salario',
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
    output_filename = 'indeed_jobs_con_habilidades_modificado.csv'
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
    print(f"   ✅ Columna 'jornada' agregada: {'jornada' in df.columns}")
    print(f"   ✅ Orden correcto de columnas: {df.columns.tolist() == orden_columnas}")

    # Estadísticas de jornada
    print(f"\n📊 ESTADÍSTICAS DE JORNADA:")
    jornada_stats = df['jornada'].value_counts(dropna=False)
    for valor, count in jornada_stats.items():
        if pd.isna(valor) or valor == '':
            print(f"   Vacíos: {count} registros ({count/len(df)*100:.1f}%)")
        else:
            print(f"   '{valor}': {count} registros ({count/len(df)*100:.1f}%)")

    # Mostrar distribución por área y jornada
    print(f"\n📊 DISTRIBUCIÓN POR ÁREA:")
    for area in df['Area'].unique():
        area_data = df[df['Area'] == area]
        tiempo_completo_area = (area_data['jornada'] == 'tiempo completo').sum()
        vacios_area = (area_data['jornada'] == '').sum()
        print(f"   {area}: {len(area_data)} empleos - Tiempo completo: {tiempo_completo_area}, Vacíos: {vacios_area}")

    return df

if __name__ == "__main__":
    df_resultado = modificar_indeed_csv()

    print("\n" + "="*50)
    print("✅ MODIFICACIONES COMPLETADAS")
    print("="*50)