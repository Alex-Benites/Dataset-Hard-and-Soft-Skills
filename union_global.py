import pandas as pd
import os

def unir_todos_los_csv():
    """
    Une todos los CSV de empleos en un solo archivo con columna de origen
    """
    print("🔗 UNIENDO TODOS LOS CSV DE EMPLEOS")
    print("="*60)

    # Definir los archivos a unir con sus rutas y nombres de origen
    archivos_csv = {
        'scripts accionTrabajo/accionTrabajo_jobs_limpio.csv': 'accion trabajo',
        'scripts Bing/bing_jobs_limpio.csv': 'bing',
        'scripts indeed/indeed_jobs_limpio.csv': 'indeed',
        'scripts multitrabajo/multitrabajos_jobs_limpio.csv': 'multitrabajos',
        'scripts opcionEmpleo/opcionEmpleo_jobs_limpio.csv': 'opcion empleo'
    }

    # Lista para almacenar todos los DataFrames
    dataframes = []

    # Cargar cada archivo y agregar columna de origen
    for archivo, nombre_pagina in archivos_csv.items():
        try:
            print(f"\n📂 Cargando: {archivo}")

            # Verificar si el archivo existe
            if os.path.exists(archivo):
                df = pd.read_csv(archivo)

                # Agregar columna 'pagina' con el nombre de origen
                df['pagina'] = nombre_pagina

                print(f"   ✅ Registros cargados: {len(df)}")
                print(f"   📋 Columnas: {df.columns.tolist()}")

                # Verificar estructura
                columnas_esperadas = ['titulo', 'empresa', 'ubicacion', 'salario', 'modalidad',
                                    'jornada', 'Area', 'habilidades_hard', 'habilidades_soft', 'pagina']

                if df.columns.tolist() == columnas_esperadas:
                    print(f"   ✅ Estructura correcta")
                    dataframes.append(df)
                else:
                    print(f"   ⚠️  Estructura diferente: {df.columns.tolist()}")
                    # Mostrar qué columnas faltan o sobran
                    faltantes = set(columnas_esperadas) - set(df.columns.tolist())
                    extras = set(df.columns.tolist()) - set(columnas_esperadas)
                    if faltantes:
                        print(f"       Columnas faltantes: {faltantes}")
                    if extras:
                        print(f"       Columnas extra: {extras}")
            else:
                print(f"   ❌ No se encontró el archivo: {archivo}")
                # Listar archivos disponibles en esa carpeta
                carpeta = os.path.dirname(archivo)
                if os.path.exists(carpeta):
                    archivos_disponibles = [f for f in os.listdir(carpeta) if f.endswith('.csv')]
                    print(f"   📁 Archivos CSV disponibles en {carpeta}: {archivos_disponibles}")

        except Exception as e:
            print(f"   ❌ Error al cargar {archivo}: {str(e)}")

    # Verificar que se cargaron archivos
    if len(dataframes) == 0:
        print(f"\n❌ No se pudo cargar ningún archivo. Verificando estructura de carpetas...")

        # Mostrar estructura actual
        print(f"\n📁 ESTRUCTURA DE CARPETAS ENCONTRADA:")
        for carpeta in ['scripts accionTrabajo', 'scripts Bing', 'scripts indeed',
                       'scripts multitrabajo', 'scripts opcionEmpleo']:
            if os.path.exists(carpeta):
                archivos = [f for f in os.listdir(carpeta) if f.endswith('.csv')]
                print(f"   {carpeta}: {archivos}")
            else:
                print(f"   {carpeta}: [NO EXISTE]")
        return None

    if len(dataframes) != len(archivos_csv):
        print(f"\n⚠️  Solo se cargaron {len(dataframes)} de {len(archivos_csv)} archivos")

    # Unir todos los DataFrames
    print(f"\n🔗 UNIENDO {len(dataframes)} ARCHIVOS...")
    df_final = pd.concat(dataframes, ignore_index=True)

    # Reordenar columnas para poner 'pagina' después de 'Area'
    columnas_finales = [
        'titulo', 'empresa', 'ubicacion', 'salario', 'modalidad',
        'jornada', 'Area', 'pagina', 'habilidades_hard', 'habilidades_soft'
    ]
    df_final = df_final[columnas_finales]

    # Guardar archivo final
    archivo_final = 'empleos_unidos_completo.csv'
    df_final.to_csv(archivo_final, index=False, encoding='utf-8-sig')

    print(f"\n✅ ARCHIVO FINAL CREADO: {archivo_final}")
    print(f"📊 ESTADÍSTICAS FINALES:")
    print(f"   Total de registros: {len(df_final)}")
    print(f"   Total de columnas: {len(df_final.columns)}")
    print(f"   Columnas: {df_final.columns.tolist()}")

    # Mostrar distribución por página
    print(f"\n📊 DISTRIBUCIÓN POR PÁGINA:")
    distribucion = df_final['pagina'].value_counts()
    for pagina, cantidad in distribucion.items():
        porcentaje = (cantidad / len(df_final)) * 100
        print(f"   {pagina}: {cantidad} registros ({porcentaje:.1f}%)")

    # Mostrar distribución por área
    print(f"\n📊 DISTRIBUCIÓN POR ÁREA:")
    areas = df_final['Area'].value_counts()
    for area, cantidad in areas.items():
        porcentaje = (cantidad / len(df_final)) * 100
        print(f"   {area}: {cantidad} registros ({porcentaje:.1f}%)")

    # Mostrar muestra del archivo final
    print(f"\n📋 MUESTRA DEL ARCHIVO FINAL:")
    muestra = df_final.head(3)[['titulo', 'empresa', 'Area', 'pagina']]
    print(muestra.to_string(index=False))

    # Verificar integridad de datos
    print(f"\n🔍 VERIFICACIÓN DE INTEGRIDAD:")
    print(f"   Registros con título vacío: {df_final['titulo'].isna().sum()}")
    print(f"   Registros con área vacía: {df_final['Area'].isna().sum()}")
    print(f"   Registros con página vacía: {df_final['pagina'].isna().sum()}")

    # Mostrar estadísticas por combinación área-página
    print(f"\n📊 MATRIZ ÁREA vs PÁGINA:")
    matriz = pd.crosstab(df_final['Area'], df_final['pagina'], margins=True)
    print(matriz)

    return df_final

if __name__ == "__main__":
    resultado = unir_todos_los_csv()

    if resultado is not None:
        print("\n" + "="*60)
        print("✅ UNIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        print(f"🎯 Archivo final: empleos_unidos_completo.csv")
        print(f"📊 Total de empleos: {len(resultado)}")
    else:
        print("\n" + "="*60)
        print("❌ ERROR EN LA UNIÓN")
        print("="*60)