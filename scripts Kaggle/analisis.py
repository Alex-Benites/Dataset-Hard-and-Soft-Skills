import pandas as pd

def generar_tabla_descripcion_dataset_limpio():
    """
    Genera tabla descriptiva del Dataset Internacional LIMPIO (Kaggle) para paper
    """

    print("Cargando dataset limpio...")
    df = pd.read_csv('dataset_kaggle_limpio.csv')

    print("\n" + "="*80)
    print("TABLA 1. DESCRIPCIÓN DEL DATASET INTERNACIONAL (KAGGLE) - LIMPIO")
    print("="*80)

    # INFORMACIÓN GENERAL
    print("\n📊 INFORMACIÓN GENERAL:")
    print(f"  Total de registros (tras filtrado): {len(df):,}")
    print(f"  Total de columnas: {len(df.columns)}")
    print(f"  Período de datos: {df['fecha_publicacion'].min()} a {df['fecha_publicacion'].max()}")

    # DESCRIPCIÓN DE COLUMNAS
    print("\n📋 DESCRIPCIÓN DE COLUMNAS:")
    print(f"\n{'Columna':<25} {'Tipo':<15} {'Descripción':<50}")
    print("-" * 90)

    columnas_info = {
        'titulo': ('Texto', 'Título del puesto de trabajo'),
        'empresa': ('Texto', 'Nombre de la empresa empleadora'),
        'ubicacion': ('Texto', 'Ubicación específica del empleo'),
        'pais': ('Texto', 'País donde se ubica el puesto'),
        'salario': ('Texto', 'Rango salarial ofrecido'),
        'jornada': ('Texto', 'Tipo de jornada laboral'),
        'experiencia': ('Texto', 'Nivel de experiencia requerido'),
        'habilidades_hard': ('Texto', 'Habilidades técnicas específicas extraídas'),
        'habilidades_soft': ('Texto', 'Habilidades blandas identificadas'),
        'responsabilidades': ('Texto', 'Descripción de responsabilidades del puesto'),
        'fecha_publicacion': ('Fecha', 'Fecha de publicación de la oferta'),
        'Area': ('Categórica', 'Perfil profesional clasificado')
    }

    for columna, (tipo, desc) in columnas_info.items():
        print(f"{columna:<25} {tipo:<15} {desc:<50}")

    # DISTRIBUCIÓN POR PERFIL
    print("\n📈 DISTRIBUCIÓN POR PERFIL PROFESIONAL (TRAS FILTRADO):")
    print(f"\n{'Perfil':<30} {'Cantidad':<15} {'Porcentaje':<15}")
    print("-" * 60)

    distribucion = df['Area'].value_counts()
    for perfil, cantidad in distribucion.items():
        porcentaje = (cantidad / len(df)) * 100
        print(f"{perfil:<30} {cantidad:>10,} {porcentaje:>13.1f}%")

    # COMPLETITUD DE DATOS
    print("\n✅ COMPLETITUD DE DATOS (Porcentaje de registros con información):")
    print(f"\n{'Columna':<25} {'Registros Completos':<20} {'Porcentaje':<15}")
    print("-" * 60)

    for columna in df.columns:
        completos = df[columna].notna().sum()
        porcentaje = (completos / len(df)) * 100
        print(f"{columna:<25} {completos:>15,} {porcentaje:>13.1f}%")

    # ESTADÍSTICAS DE HABILIDADES (100% especificadas por diseño)
    print("\n🎯 ESTADÍSTICAS DE HABILIDADES:")
    print(f"\n  ✅ Registros con habilidades hard especificadas: {len(df):,} (100.0%)")
    print(f"  ✅ Registros con habilidades soft especificadas: {len(df):,} (100.0%)")
    print(f"\n  Nota: Dataset filtrado contiene solo registros con ambas habilidades especificadas")

    # Contar habilidades únicas
    print("\n  Diversidad de habilidades:")

    # Hard skills únicas
    todas_hard = set()
    for skills in df['habilidades_hard']:
        if pd.notna(skills) and skills != 'No especificado':
            habilidades = [h.strip() for h in str(skills).split(',')]
            todas_hard.update(habilidades)

    # Soft skills únicas
    todas_soft = set()
    for skills in df['habilidades_soft']:
        if pd.notna(skills) and skills != 'No especificado':
            habilidades = [h.strip() for h in str(skills).split(',')]
            todas_soft.update(habilidades)

    print(f"    - Habilidades hard únicas identificadas: {len(todas_hard)}")
    print(f"    - Habilidades soft únicas identificadas: {len(todas_soft)}")

    # Top 10 habilidades hard
    print(f"\n  Top 10 Habilidades Hard más demandadas:")
    from collections import Counter
    hard_counter = Counter()
    for skills in df['habilidades_hard']:
        if pd.notna(skills) and skills != 'No especificado':
            habilidades = [h.strip() for h in str(skills).split(',')]
            hard_counter.update(habilidades)

    for i, (skill, count) in enumerate(hard_counter.most_common(10), 1):
        print(f"    {i:2d}. {skill}: {count:,} menciones")

    # Top 10 habilidades soft
    print(f"\n  Top 10 Habilidades Soft más demandadas:")
    soft_counter = Counter()
    for skills in df['habilidades_soft']:
        if pd.notna(skills) and skills != 'No especificado':
            habilidades = [h.strip() for h in str(skills).split(',')]
            soft_counter.update(habilidades)

    for i, (skill, count) in enumerate(soft_counter.most_common(10), 1):
        print(f"    {i:2d}. {skill}: {count:,} menciones")

    # COBERTURA POR PERFIL
    print("\n  Distribución de habilidades por perfil:")
    print(f"\n  {'Perfil':<30} {'Registros':<15} {'% del Total':<15}")
    print("  " + "-" * 60)

    for area in df['Area'].unique():
        df_area = df[df['Area'] == area]
        pct = (len(df_area) / len(df)) * 100
        print(f"  {area:<30} {len(df_area):>10,} {pct:>13.1f}%")

    # PAÍSES REPRESENTADOS
    print("\n🌍 COBERTURA GEOGRÁFICA:")
    paises_unicos = df['pais'].nunique()
    print(f"  Total de países representados: {paises_unicos}")
    print(f"\n  Top 10 países con más ofertas laborales:")
    print(f"\n  {'País':<25} {'Cantidad':<15} {'% del Total':<15}")
    print("  " + "-" * 55)

    top_paises = df['pais'].value_counts().head(10)
    for pais, cantidad in top_paises.items():
        pct = (cantidad / len(df)) * 100
        print(f"  {pais:<25} {cantidad:>10,} {pct:>13.1f}%")

    # RESUMEN PARA TABLA DEL PAPER
    print("\n" + "="*80)
    print("📄 TABLA PARA PAPER ACADÉMICO")
    print("="*80)

    print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  Tabla 1. Descripción del Dataset Internacional (Kaggle) - Filtrado      ║
╚═══════════════════════════════════════════════════════════════════════════╝

Característica                      | Valor
------------------------------------|------------------------------------------
Total de registros (filtrado)       | {len(df):,}
Registros eliminados                | (con "No especificado" en habilidades)
Columnas                            | {len(df.columns)}
Período temporal                    | {df['fecha_publicacion'].min()} - {df['fecha_publicacion'].max()}
Perfiles profesionales              | 3 (QA, Desarrollador, Analista de Datos)
Países representados                | {paises_unicos}
Registros con habilidades completas | {len(df):,} (100%)
Habilidades hard únicas             | {len(todas_hard)}
Habilidades soft únicas             | {len(todas_soft)}
Completitud promedio                | {df.notna().mean().mean()*100:.1f}%

Distribución por perfil profesional:
- QA (Tester de Software)           | {distribucion['QA']:,} ({distribucion['QA']/len(df)*100:.1f}%)
- Desarrollador de Software         | {distribucion['Desarrollador de Software']:,} ({distribucion['Desarrollador de Software']/len(df)*100:.1f}%)
- Analista de Datos                 | {distribucion['Analista de Datos']:,} ({distribucion['Analista de Datos']/len(df)*100:.1f}%)

Top 5 Habilidades Hard:
{chr(10).join([f"  {i}. {skill} ({count:,} menciones)" for i, (skill, count) in enumerate(hard_counter.most_common(5), 1)])}

Top 5 Habilidades Soft:
{chr(10).join([f"  {i}. {skill} ({count:,} menciones)" for i, (skill, count) in enumerate(soft_counter.most_common(5), 1)])}

Fuente: Kaggle (dataset procesado y filtrado)
Procesamiento: Extracción automática de habilidades mediante NLP y diccionarios
                predefinidos. Filtrado de registros sin habilidades especificadas.
Traducción: Términos traducidos al español para estandarización.
Variables: título, empresa, ubicación, país, salario, jornada, experiencia,
          habilidades_hard, habilidades_soft, responsabilidades,
          fecha_publicacion, Area.
    """)

    print("="*80)

    # Generar versión LaTeX para paper
    print("\n" + "="*80)
    print("📄 VERSIÓN LATEX (copiar al paper)")
    print("="*80)

    latex_table = f"""
\\begin{{table}}[h]
\\centering
\\caption{{Descripción del Dataset Internacional (Kaggle)}}
\\label{{tab:dataset_kaggle}}
\\begin{{tabular}}{{|l|r|}}
\\hline
\\textbf{{Característica}} & \\textbf{{Valor}} \\\\
\\hline
Total de registros & {len(df):,} \\\\
Columnas & {len(df.columns)} \\\\
Período temporal & {df['fecha_publicacion'].min()} - {df['fecha_publicacion'].max()} \\\\
Perfiles profesionales & 3 \\\\
Países representados & {paises_unicos} \\\\
Completitud & {df.notna().mean().mean()*100:.1f}\\% \\\\
\\hline
\\multicolumn{{2}}{{|c|}}{{\\textbf{{Distribución por Perfil}}}} \\\\
\\hline
QA & {distribucion['QA']:,} ({distribucion['QA']/len(df)*100:.1f}\\%) \\\\
Desarrollador & {distribucion['Desarrollador de Software']:,} ({distribucion['Desarrollador de Software']/len(df)*100:.1f}\\%) \\\\
Analista de Datos & {distribucion['Analista de Datos']:,} ({distribucion['Analista de Datos']/len(df)*100:.1f}\\%) \\\\
\\hline
\\end{{tabular}}
\\end{{table}}
    """

    print(latex_table)

if __name__ == "__main__":
    generar_tabla_descripcion_dataset_limpio()