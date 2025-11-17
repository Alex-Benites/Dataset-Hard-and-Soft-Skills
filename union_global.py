import pandas as pd
from collections import Counter

def generar_tabla_descripcion_dataset_ecuador():
    """
    Genera tabla descriptiva del Dataset Ecuador (scraping local) para paper
    """

    print("Cargando dataset Ecuador...")
    df = pd.read_csv('Dataset_habilidades_hard_and_soft_skills.csv')

    print("\n" + "="*80)
    print("TABLA 2. DESCRIPCIÓN DEL DATASET ECUADOR (SCRAPING LOCAL)")
    print("="*80)

    # INFORMACIÓN GENERAL
    print("\n📊 INFORMACIÓN GENERAL:")
    print(f"  Total de registros: {len(df):,}")
    print(f"  Total de columnas: {len(df.columns)}")

    # DESCRIPCIÓN DE COLUMNAS
    print("\n📋 DESCRIPCIÓN DE COLUMNAS:")
    print(f"\n{'Columna':<25} {'Tipo':<15} {'Descripción':<50}")
    print("-" * 90)

    columnas_info = {
        'titulo': ('Texto', 'Título del puesto de trabajo'),
        'empresa': ('Texto', 'Nombre de la empresa empleadora'),
        'ubicacion': ('Texto', 'Ubicación específica del empleo'),
        'salario': ('Numérico', 'Salario ofrecido (USD)'),
        'modalidad': ('Texto', 'Modalidad de trabajo (remoto/presencial/híbrido)'),
        'jornada': ('Texto', 'Tipo de jornada laboral'),
        'Area': ('Categórica', 'Perfil profesional clasificado'),
        'pagina': ('Categórica', 'Portal web de origen del dato'),
        'habilidades_hard': ('Texto', 'Habilidades técnicas extraídas'),
        'habilidades_soft': ('Texto', 'Habilidades blandas extraídas')
    }

    for columna, (tipo, desc) in columnas_info.items():
        print(f"{columna:<25} {tipo:<15} {desc:<50}")

    # DISTRIBUCIÓN POR PORTAL WEB
    print("\n🌐 DISTRIBUCIÓN POR PORTAL WEB (FUENTE):")
    print(f"\n{'Portal Web':<30} {'Cantidad':<15} {'Porcentaje':<15}")
    print("-" * 60)

    distribucion_portal = df['pagina'].value_counts()
    for portal, cantidad in distribucion_portal.items():
        porcentaje = (cantidad / len(df)) * 100
        print(f"{portal:<30} {cantidad:>10,} {porcentaje:>13.1f}%")

    # DISTRIBUCIÓN POR PERFIL PROFESIONAL
    print("\n📈 DISTRIBUCIÓN POR PERFIL PROFESIONAL:")
    print(f"\n{'Perfil':<30} {'Cantidad':<15} {'Porcentaje':<15}")
    print("-" * 60)

    distribucion_area = df['Area'].value_counts()
    for area, cantidad in distribucion_area.items():
        porcentaje = (cantidad / len(df)) * 100
        print(f"{area:<30} {cantidad:>10,} {porcentaje:>13.1f}%")

    # COMPLETITUD DE DATOS
    print("\n✅ COMPLETITUD DE DATOS:")
    print(f"\n{'Columna':<25} {'Registros Completos':<20} {'Porcentaje':<15}")
    print("-" * 60)

    for columna in df.columns:
        if columna in ['habilidades_hard', 'habilidades_soft']:
            completos = len(df[df[columna] != 'No especificado'])
        else:
            completos = df[columna].notna().sum()

        porcentaje = (completos / len(df)) * 100
        print(f"{columna:<25} {completos:>15,} {porcentaje:>13.1f}%")

    # ESTADÍSTICAS DE HABILIDADES
    print("\n🎯 ESTADÍSTICAS DE HABILIDADES EXTRAÍDAS:")

    hard_especificadas = len(df[df['habilidades_hard'] != 'No especificado'])
    soft_especificadas = len(df[df['habilidades_soft'] != 'No especificado'])

    print(f"\n  Registros con habilidades hard especificadas: {hard_especificadas:,} ({hard_especificadas/len(df)*100:.1f}%)")
    print(f"  Registros con habilidades soft especificadas: {soft_especificadas:,} ({soft_especificadas/len(df)*100:.1f}%)")

    # Top habilidades por tipo
    print("\n  Top 10 Habilidades Hard más demandadas (Ecuador):")
    hard_counter = Counter()
    for skills in df['habilidades_hard']:
        if pd.notna(skills) and skills != 'No especificado':
            habilidades = [h.strip() for h in str(skills).split(',')]
            hard_counter.update(habilidades)

    for i, (skill, count) in enumerate(hard_counter.most_common(10), 1):
        print(f"    {i:2d}. {skill}: {count:,} menciones")

    print("\n  Top 10 Habilidades Soft más demandadas (Ecuador):")
    soft_counter = Counter()
    for skills in df['habilidades_soft']:
        if pd.notna(skills) and skills != 'No especificado':
            habilidades = [h.strip() for h in str(skills).split(',')]
            soft_counter.update(habilidades)

    for i, (skill, count) in enumerate(soft_counter.most_common(10), 1):
        print(f"    {i:2d}. {skill}: {count:,} menciones")

    # COBERTURA GEOGRÁFICA
    print("\n📍 COBERTURA GEOGRÁFICA (ECUADOR):")
    ubicaciones_unicas = df['ubicacion'].nunique()
    print(f"  Ubicaciones únicas: {ubicaciones_unicas}")

    print(f"\n  Top 10 ubicaciones con más ofertas:")
    print(f"\n  {'Ubicación':<35} {'Cantidad':<15}")
    print("  " + "-" * 50)

    top_ubicaciones = df['ubicacion'].value_counts().head(10)
    for ubicacion, cantidad in top_ubicaciones.items():
        print(f"  {str(ubicacion)[:35]:<35} {cantidad:>10,}")

    # ANÁLISIS DE SALARIOS
    print("\n💰 ANÁLISIS SALARIAL:")
    salarios_validos = df[df['salario'].notna()]

    if len(salarios_validos) > 0:
        print(f"  Registros con salario especificado: {len(salarios_validos):,} ({len(salarios_validos)/len(df)*100:.1f}%)")
        print(f"  Salario promedio: ${salarios_validos['salario'].mean():.2f} USD")
        print(f"  Salario mediana: ${salarios_validos['salario'].median():.2f} USD")
        print(f"  Salario mínimo: ${salarios_validos['salario'].min():.2f} USD")
        print(f"  Salario máximo: ${salarios_validos['salario'].max():.2f} USD")
    else:
        print(f"  No hay datos salariales disponibles")

    # MATRIZ PERFIL vs PORTAL
    print("\n📊 MATRIZ: PERFIL vs PORTAL WEB:")
    matriz = pd.crosstab(df['Area'], df['pagina'], margins=True)
    print(matriz)

    # RESUMEN PARA TABLA DEL PAPER
    print("\n" + "="*80)
    print("📄 RESUMEN PARA TABLA DEL PAPER")
    print("="*80)

    total_portales = df['pagina'].nunique()

    print(f"""
Tabla 2. Descripción del Dataset Ecuador (Web Scraping)

Característica                      | Valor
------------------------------------|------------------------------------------
Total de registros                  | {len(df):,}
Columnas                            | {len(df.columns)}
Portales web scrapeados             | {total_portales} ({', '.join(df['pagina'].unique())})
Perfiles profesionales              | 3 (QA, Desarrollador, Analista de Datos)
Ubicaciones en Ecuador              | {ubicaciones_unicas}
Registros con habilidades hard      | {hard_especificadas:,} ({hard_especificadas/len(df)*100:.1f}%)
Registros con habilidades soft      | {soft_especificadas:,} ({soft_especificadas/len(df)*100:.1f}%)
Registros con salario especificado  | {len(salarios_validos):,} ({len(salarios_validos)/len(df)*100:.1f}%)
Completitud promedio                | {df.notna().mean().mean()*100:.1f}%

Distribución por portal web:
{chr(10).join([f"- {portal}: {count:,} ({count/len(df)*100:.1f}%)" for portal, count in distribucion_portal.items()])}

Distribución por perfil:
{chr(10).join([f"- {area}: {count:,} ({count/len(df)*100:.1f}%)" for area, count in distribucion_area.items()])}

Top 5 Habilidades Hard (Ecuador):
{chr(10).join([f"  {i}. {skill} ({count:,} menciones)" for i, (skill, count) in enumerate(hard_counter.most_common(5), 1)])}

Top 5 Habilidades Soft (Ecuador):
{chr(10).join([f"  {i}. {skill} ({count:,} menciones)" for i, (skill, count) in enumerate(soft_counter.most_common(5), 1)])}

Metodología: Web scraping con Selenium y BeautifulSoup
Fuentes: {', '.join(df['pagina'].unique())}
Período de recolección: [Especificar fechas]
Variables: título, empresa, ubicación, salario, modalidad, jornada, área profesional,
          portal web, habilidades técnicas (hard), habilidades blandas (soft).
Procesamiento: Extracción automática mediante NLP y diccionarios predefinidos.
    """)

    print("="*80)

    # Generar versión LaTeX
    print("\n" + "="*80)
    print("📄 VERSIÓN LATEX (copiar al paper)")
    print("="*80)

    latex_table = f"""
\\begin{{table}}[h]
\\centering
\\caption{{Descripción del Dataset Ecuador (Web Scraping)}}
\\label{{tab:dataset_ecuador}}
\\begin{{tabular}}{{|l|r|}}
\\hline
\\textbf{{Característica}} & \\textbf{{Valor}} \\\\
\\hline
Total de registros & {len(df):,} \\\\
Columnas & {len(df.columns)} \\\\
Portales web & {total_portales} \\\\
Perfiles profesionales & 3 \\\\
Ubicaciones en Ecuador & {ubicaciones_unicas} \\\\
Completitud & {df.notna().mean().mean()*100:.1f}\\% \\\\
\\hline
\\multicolumn{{2}}{{|c|}}{{\\textbf{{Distribución por Perfil}}}} \\\\
\\hline
{chr(10).join([f"{area} & {count:,} ({count/len(df)*100:.1f}\\%) \\\\" for area, count in distribucion_area.items()])}
\\hline
\\multicolumn{{2}}{{|c|}}{{\\textbf{{Distribución por Portal}}}} \\\\
\\hline
{chr(10).join([f"{portal} & {count:,} ({count/len(df)*100:.1f}\\%) \\\\" for portal, count in distribucion_portal.items()])}
\\hline
\\end{{tabular}}
\\end{{table}}
    """

    print(latex_table)

if __name__ == "__main__":
    generar_tabla_descripcion_dataset_ecuador()