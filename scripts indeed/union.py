import pandas as pd

# Leer los tres archivos CSV
df_analista_datos = pd.read_csv('indeed_jobs_analista_datos.csv')
df_qa = pd.read_csv('indeed_jobs_qa.csv')
df_desarrolladores = pd.read_csv('indeed_jobs_desarrolladores.csv')

# Verificar las columnas de cada archivo
print("Columnas en Analista de Datos:")
print(df_analista_datos.columns.tolist())
print(f"Cantidad de filas: {len(df_analista_datos)}")

print("\nColumnas en QA:")
print(df_qa.columns.tolist())
print(f"Cantidad de filas: {len(df_qa)}")

print("\nColumnas en Desarrolladores:")
print(df_desarrolladores.columns.tolist())
print(f"Cantidad de filas: {len(df_desarrolladores)}")

# Verificar si todas las columnas esperadas están presentes
columnas_esperadas = ['titulo', 'empresa', 'ubicacion', 'salario', 'tipo_contrato', 'modalidad', 'descripcion']

print("\n¿Todas las columnas esperadas están presentes?")
for archivo, df in [("Analista de Datos", df_analista_datos), ("QA", df_qa), ("Desarrolladores", df_desarrolladores)]:
    columnas_presentes = [col for col in columnas_esperadas if col in df.columns]
    columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]
    print(f"{archivo}: {len(columnas_presentes)}/{len(columnas_esperadas)} columnas presentes")
    if columnas_faltantes:
        print(f"  Faltantes: {columnas_faltantes}")

# CAMBIO: Incluir "Area" en las columnas finales
columnas_finales = ['titulo', 'empresa', 'ubicacion', 'salario', 'tipo_contrato', 'modalidad', 'descripcion', 'Area']

# Extraer solo las columnas disponibles de cada archivo
df_analista_final = df_analista_datos[[col for col in columnas_esperadas if col in df_analista_datos.columns]]
df_qa_final = df_qa[[col for col in columnas_esperadas if col in df_qa.columns]]
df_desarrolladores_final = df_desarrolladores[[col for col in columnas_esperadas if col in df_desarrolladores.columns]]

# CAMBIO: Agregar la columna "Area" a cada DataFrame
df_analista_final['Area'] = 'Analista de Datos'
df_qa_final['Area'] = 'QA'
df_desarrolladores_final['Area'] = 'Desarrollador de Software'

print(f"\n✅ Columna 'Area' agregada:")
print(f"   Analista de Datos: {len(df_analista_final)} registros con Area = 'Analista de Datos'")
print(f"   QA: {len(df_qa_final)} registros con Area = 'QA'")
print(f"   Desarrolladores: {len(df_desarrolladores_final)} registros con Area = 'Desarrollador de Software'")

# Añadir columnas faltantes con valores nulos si es necesario (excluyendo "Area" que ya se agregó)
for df_temp, nombre in [(df_analista_final, "analista"), (df_qa_final, "qa"), (df_desarrolladores_final, "dev")]:
    for col in columnas_esperadas:  # Solo las columnas esperadas originales
        if col not in df_temp.columns:
            df_temp[col] = None
            print(f"Agregada columna '{col}' a {nombre} con valores nulos")

# Asegurar que todas tengan las mismas columnas en el mismo orden
df_analista_final = df_analista_final[columnas_finales]
df_qa_final = df_qa_final[columnas_finales]
df_desarrolladores_final = df_desarrolladores_final[columnas_finales]

# Unir los tres DataFrames
df_combinado = pd.concat([df_analista_final, df_qa_final, df_desarrolladores_final], ignore_index=True)

# Verificar el resultado
print("\nInformación del archivo combinado:")
print(f"Total de filas: {len(df_combinado)}")
print(f"Columnas: {df_combinado.columns.tolist()}")

# Mostrar un resumen de cada categoría
print("\nResumen por tipo de trabajo:")
print(f"Analista de Datos: {len(df_analista_datos)} trabajos")
print(f"QA: {len(df_qa)} trabajos")
print(f"Desarrolladores: {len(df_desarrolladores)} trabajos")
print(f"Total combinado: {len(df_combinado)} trabajos")

# CAMBIO: Mostrar resumen por área
print("\n📊 RESUMEN POR ÁREA:")
area_counts = df_combinado['Area'].value_counts()
for area, count in area_counts.items():
    print(f"   {area}: {count} trabajos")

# Guardar el archivo combinado
df_combinado.to_csv('indeed_jobs_todos_trabajos_tech.csv', index=False, encoding='utf-8-sig')

print(f"\n✅ Archivo guardado exitosamente como 'indeed_jobs_todos_trabajos_tech.csv'")
print(f"📊 Total de registros: {len(df_combinado)}")

# Mostrar estadísticas por columna
print("\n📊 ESTADÍSTICAS POR COLUMNA:")
for col in columnas_finales:
    valores_no_nulos = df_combinado[col].notna().sum()
    valores_nulos = df_combinado[col].isna().sum()
    print(f"   {col}: {valores_no_nulos} completos, {valores_nulos} vacíos")

# CAMBIO: Mostrar muestra incluyendo la columna "Area"
print("\n📋 Muestra de los primeros 3 registros:")
print(df_combinado.head(3)[['titulo', 'empresa', 'ubicacion', 'modalidad', 'Area']].to_string())

# CAMBIO: Mostrar una muestra de cada área
print("\n📋 Muestra por área:")
for area in df_combinado['Area'].unique():
    print(f"\n--- {area} ---")
    muestra = df_combinado[df_combinado['Area'] == area].head(1)
    print(muestra[['titulo', 'empresa', 'Area']].to_string(index=False))