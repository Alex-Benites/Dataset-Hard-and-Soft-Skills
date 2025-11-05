import pandas as pd

# Leer los tres archivos CSV
df_qa = pd.read_csv('opcion_empleo_qa.csv')
df_desarrolladores = pd.read_csv('opcion_empleo_desarrolladores.csv')
df_analista_datos = pd.read_csv('opcion_empleo_analista_datos.csv')

# Verificar las columnas de cada archivo
print("Columnas en QA:")
print(df_qa.columns.tolist())
print(f"Cantidad de filas: {len(df_qa)}")

print("\nColumnas en Desarrolladores:")
print(df_desarrolladores.columns.tolist())
print(f"Cantidad de filas: {len(df_desarrolladores)}")

print("\nColumnas en Analista de Datos:")
print(df_analista_datos.columns.tolist())
print(f"Cantidad de filas: {len(df_analista_datos)}")

# Verificar si todas las columnas coinciden con las esperadas
columnas_esperadas = ['index', 'titulo', 'empresa', 'ubicacion', 'salario', 'modalidad', 'jornada', 'tipo_contrato', 'fecha_publicacion', 'descripcion', 'url']

qa_columns = set(df_qa.columns)
dev_columns = set(df_desarrolladores.columns)
data_columns = set(df_analista_datos.columns)

print("\n¿Todas las columnas coinciden con las esperadas?")
print(f"QA vs esperadas: {qa_columns == set(columnas_esperadas)}")
print(f"Desarrolladores vs esperadas: {dev_columns == set(columnas_esperadas)}")
print(f"Analista datos vs esperadas: {data_columns == set(columnas_esperadas)}")

# CAMBIO 1: Extraer solo las columnas necesarias (sin index, fecha_publicacion, url)
columnas_trabajo = ['titulo', 'empresa', 'ubicacion', 'salario', 'modalidad', 'jornada', 'tipo_contrato', 'descripcion']

# Verificar que todas las columnas de trabajo estén presentes
df_qa_final = df_qa[[col for col in columnas_trabajo if col in df_qa.columns]]
df_desarrolladores_final = df_desarrolladores[[col for col in columnas_trabajo if col in df_desarrolladores.columns]]
df_analista_final = df_analista_datos[[col for col in columnas_trabajo if col in df_analista_datos.columns]]

# CAMBIO 2: Agregar la columna "Area" a cada DataFrame
df_qa_final['Area'] = 'QA'
df_desarrolladores_final['Area'] = 'Desarrollador de Software'
df_analista_final['Area'] = 'Analista de Datos'

print(f"\n✅ Columna 'Area' agregada:")
print(f"   QA: {len(df_qa_final)} registros con Area = 'QA'")
print(f"   Desarrolladores: {len(df_desarrolladores_final)} registros con Area = 'Desarrollador de Software'")
print(f"   Analista de Datos: {len(df_analista_final)} registros con Area = 'Analista de Datos'")

# Añadir columnas faltantes con valores nulos si es necesario
for df_temp, nombre in [(df_qa_final, "qa"), (df_desarrolladores_final, "desarrolladores"), (df_analista_final, "analista")]:
    for col in columnas_trabajo:  # Solo las columnas de trabajo
        if col not in df_temp.columns:
            df_temp[col] = None
            print(f"Agregada columna '{col}' a {nombre} con valores nulos")

# CAMBIO 3: Definir las columnas finales (incluyendo Area)
columnas_finales = ['titulo', 'empresa', 'ubicacion', 'salario', 'modalidad', 'jornada', 'tipo_contrato', 'descripcion', 'Area']

# Asegurar que todas tengan las mismas columnas en el mismo orden
df_qa_final = df_qa_final[columnas_finales]
df_desarrolladores_final = df_desarrolladores_final[columnas_finales]
df_analista_final = df_analista_final[columnas_finales]

# Unir los tres DataFrames
df_combinado = pd.concat([df_qa_final, df_desarrolladores_final, df_analista_final], ignore_index=True)

# Verificar el resultado
print("\nInformación del archivo combinado:")
print(f"Total de filas: {len(df_combinado)}")
print(f"Columnas: {df_combinado.columns.tolist()}")

# Mostrar un resumen de cada categoría
print("\nResumen por tipo de trabajo:")
print(f"QA: {len(df_qa)} trabajos")
print(f"Desarrolladores: {len(df_desarrolladores)} trabajos")
print(f"Analista de Datos: {len(df_analista_datos)} trabajos")
print(f"Total combinado: {len(df_combinado)} trabajos")

# CAMBIO 4: Mostrar resumen por área
print("\n📊 RESUMEN POR ÁREA:")
area_counts = df_combinado['Area'].value_counts()
for area, count in area_counts.items():
    print(f"   {area}: {count} trabajos")

# CAMBIO 5: Guardar el archivo combinado con nombre específico para OpciónEmpleo
df_combinado.to_csv('opcion_empleo_todos_trabajos_tech.csv', index=False, encoding='utf-8-sig')

print(f"\n✅ Archivo guardado exitosamente como 'opcion_empleo_todos_trabajos_tech.csv'")
print(f"📊 Total de registros: {len(df_combinado)}")

# Mostrar estadísticas por columna
print("\n📊 ESTADÍSTICAS POR COLUMNA:")
for col in columnas_finales:
    valores_no_nulos = df_combinado[col].notna().sum()
    valores_nulos = df_combinado[col].isna().sum()
    print(f"   {col}: {valores_no_nulos} completos, {valores_nulos} vacíos")

# CAMBIO 6: Mostrar muestra incluyendo la columna "Area"
print("\n📋 Muestra de los primeros 3 registros:")
print(df_combinado.head(3)[['titulo', 'empresa', 'ubicacion', 'modalidad', 'Area']].to_string())

# CAMBIO 7: Mostrar una muestra de cada área
print("\n📋 Muestra por área:")
for area in df_combinado['Area'].unique():
    print(f"\n--- {area} ---")
    muestra = df_combinado[df_combinado['Area'] == area].head(1)
    if not muestra.empty:
        print(muestra[['titulo', 'empresa', 'Area']].to_string(index=False))
    else:
        print("No hay datos disponibles")