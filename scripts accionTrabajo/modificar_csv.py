import pandas as pd

def convertir_salarios_a_enteros():
    """
    Convierte todos los salarios de formato decimal a entero en el CSV de AcciónTrabajo
    """
    print("🔢 CONVIRTIENDO SALARIOS A ENTEROS")
    print("="*50)

    # Leer el CSV
    try:
        df = pd.read_csv('accionTrabajo_jobs_con_habilidades_final.csv')
        print(f"✅ Archivo leído exitosamente: {len(df)} registros")
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'accionTrabajo_jobs_con_habilidades_final.csv'")
        return

    # Mostrar algunos ejemplos de salarios antes de la conversión
    print(f"\n🔍 SALARIOS ANTES DE LA CONVERSIÓN:")
    salarios_con_valor = df[df['salario'].notna() & (df['salario'] != '')]
    print(f"Registros con salario: {len(salarios_con_valor)}")

    if len(salarios_con_valor) > 0:
        print("Ejemplos de salarios actuales:")
        for i, (_, row) in enumerate(salarios_con_valor.head(5).iterrows()):
            print(f"   {i+1}. {row['titulo'][:40]}... → {row['salario']} (tipo: {type(row['salario'])})")

    # Función para convertir salario a entero
    def convertir_a_entero(salario):
        """
        Convierte el salario a entero, manejando diferentes formatos
        """
        if pd.isna(salario) or salario == '' or salario == 0:
            return ''

        try:
            # Convertir a float primero para manejar decimales, luego a int
            salario_float = float(salario)
            if salario_float == 0:
                return ''
            return str(int(salario_float))
        except (ValueError, TypeError):
            # Si no se puede convertir, devolver vacío
            return ''

    # Aplicar la conversión
    print(f"\n🔄 APLICANDO CONVERSIÓN A ENTEROS...")
    df['salario'] = df['salario'].apply(convertir_a_entero)

    # Mostrar resultados después de la conversión
    print(f"\n✅ SALARIOS DESPUÉS DE LA CONVERSIÓN:")
    salarios_con_valor_nuevos = df[df['salario'] != '']
    salarios_vacios = df[df['salario'] == '']

    print(f"   Con valor entero: {len(salarios_con_valor_nuevos)} registros")
    print(f"   Vacíos: {len(salarios_vacios)} registros")

    if len(salarios_con_valor_nuevos) > 0:
        print(f"\n📊 EJEMPLOS DE SALARIOS CONVERTIDOS:")
        for i, (_, row) in enumerate(salarios_con_valor_nuevos.head(10).iterrows()):
            print(f"   {i+1}. {row['titulo'][:40]}... → {row['salario']}")

        # Estadísticas
        salarios_numericos = [int(s) for s in salarios_con_valor_nuevos['salario'] if s.isdigit()]
        if salarios_numericos:
            print(f"\n📈 ESTADÍSTICAS DE SALARIOS:")
            print(f"   Salario mínimo: ${min(salarios_numericos)}")
            print(f"   Salario máximo: ${max(salarios_numericos)}")
            print(f"   Salario promedio: ${sum(salarios_numericos)//len(salarios_numericos)}")

    # Guardar el archivo modificado
    output_filename = 'accionTrabajo_jobs_con_habilidades_final.csv'
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"\n✅ Archivo guardado: {output_filename}")

    # Verificar tipos de datos
    print(f"\n🔍 VERIFICACIÓN DE TIPOS:")
    ejemplos_verificacion = df[df['salario'] != ''].head(3)
    for _, row in ejemplos_verificacion.iterrows():
        print(f"   '{row['salario']}' → Tipo: {type(row['salario'])}")

    # Mostrar resumen final
    print(f"\n📋 RESUMEN FINAL:")
    print(f"   Total de registros: {len(df)}")
    print(f"   Salarios convertidos a enteros: {len(salarios_con_valor_nuevos)}")
    print(f"   Salarios que quedaron vacíos: {len(salarios_vacios)}")

    return df

if __name__ == "__main__":
    resultado = convertir_salarios_a_enteros()

    print("\n" + "="*50)
    print("✅ CONVERSIÓN COMPLETADA")
    print("="*50)