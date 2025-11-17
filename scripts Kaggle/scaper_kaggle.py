import pandas as pd
import re
from tqdm import tqdm

def extraer_puestos_por_perfil():
    """
    Extrae puestos de trabajo por perfil profesional del archivo job_descriptions.csv
    y los separa en CSVs individuales
    """

    print("Cargando dataset principal...")
    # Cargar el dataset principal
    try:
        df = pd.read_csv('job_descriptions.csv', low_memory=False)
        print(f"Dataset cargado exitosamente: {len(df)} registros")
        print(f"Columnas disponibles: {list(df.columns)}")
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return

    # Definir patrones de búsqueda para cada perfil
    patrones_qa = [
        r'(?i)\bQA\b', r'(?i)Quality Assurance', r'(?i)Quality Control',
        r'(?i)\bTest\w*', r'(?i)Software Tester', r'(?i)Manual Tester',
        r'(?i)Automation Tester', r'(?i)QC\b', r'(?i)Test Engineer'
    ]

    patrones_developer = [
        r'(?i)Developer', r'(?i)Desarrollador', r'(?i)Software Engineer',
        r'(?i)Programmer', r'(?i)Frontend', r'(?i)Backend', r'(?i)Full Stack',
        r'(?i)Web Developer', r'(?i)Mobile Developer', r'(?i)Software Dev'
    ]

    patrones_data_analyst = [
        r'(?i)Data Analyst', r'(?i)Analista de Datos', r'(?i)Data Scientist',
        r'(?i)Business Analyst', r'(?i)Business Intelligence', r'(?i)BI Analyst',
        r'(?i)Analytics', r'(?i)Data Engineer', r'(?i)Reporting Analyst'
    ]

    def buscar_patron_en_fila(fila, patrones):
        """Busca patrones en las columnas relevantes de una fila"""
        campos_busqueda = ['Job Title', 'Role', 'Job Description', 'Skills', 'Responsibilities']
        texto_completo = ""

        for campo in campos_busqueda:
            if campo in fila.index and pd.notna(fila[campo]):
                texto_completo += str(fila[campo]) + " "

        for patron in patrones:
            if re.search(patron, texto_completo):
                return True
        return False

    # Filtrar datos por perfil
    print("\nFiltrando puestos por perfil...")

    # QA/Testing
    print("Filtrando puestos de QA/Testing...")
    qa_mask = df.apply(lambda row: buscar_patron_en_fila(row, patrones_qa), axis=1)
    df_qa = df[qa_mask].copy()
    df_qa['Perfil'] = 'QA/Testing'

    # Developer
    print("Filtrando puestos de Developer...")
    dev_mask = df.apply(lambda row: buscar_patron_en_fila(row, patrones_developer), axis=1)
    df_developer = df[dev_mask].copy()
    df_developer['Perfil'] = 'Developer'

    # Data Analyst
    print("Filtrando puestos de Data Analyst...")
    da_mask = df.apply(lambda row: buscar_patron_en_fila(row, patrones_data_analyst), axis=1)
    df_data_analyst = df[da_mask].copy()
    df_data_analyst['Perfil'] = 'Data Analyst'

    # Mostrar estadísticas
    print(f"\n=== ESTADÍSTICAS DE FILTRADO ===")
    print(f"QA/Testing: {len(df_qa)} registros")
    print(f"Developer: {len(df_developer)} registros")
    print(f"Data Analyst: {len(df_data_analyst)} registros")
    print(f"Total registros filtrados: {len(df_qa) + len(df_developer) + len(df_data_analyst)}")

    # Guardar CSVs separados
    print(f"\n=== GUARDANDO ARCHIVOS CSV ===")

    # Guardar cada perfil por separado
    if len(df_qa) > 0:
        df_qa.to_csv('puestos_qa_testing.csv', index=False)
        print(f"✓ Guardado: puestos_qa_testing.csv ({len(df_qa)} registros)")

    if len(df_developer) > 0:
        df_developer.to_csv('puestos_developer.csv', index=False)
        print(f"✓ Guardado: puestos_developer.csv ({len(df_developer)} registros)")

    if len(df_data_analyst) > 0:
        df_data_analyst.to_csv('puestos_data_analyst.csv', index=False)
        print(f"✓ Guardado: puestos_data_analyst.csv ({len(df_data_analyst)} registros)")

    # Crear un CSV consolidado con todos los perfiles
    print(f"\nCreando archivo consolidado...")
    df_consolidado = pd.concat([df_qa, df_developer, df_data_analyst], ignore_index=True)
    df_consolidado.to_csv('puestos_consolidado_tres_perfiles.csv', index=False)
    print(f"✓ Guardado: puestos_consolidado_tres_perfiles.csv ({len(df_consolidado)} registros)")

    # Mostrar muestra de cada perfil
    print(f"\n=== MUESTRA DE DATOS ===")

    if len(df_qa) > 0:
        print(f"\nMuestra QA/Testing (primeros 3 títulos):")
        for i, titulo in enumerate(df_qa['Job Title'].head(3)):
            print(f"  {i+1}. {titulo}")

    if len(df_developer) > 0:
        print(f"\nMuestra Developer (primeros 3 títulos):")
        for i, titulo in enumerate(df_developer['Job Title'].head(3)):
            print(f"  {i+1}. {titulo}")

    if len(df_data_analyst) > 0:
        print(f"\nMuestra Data Analyst (primeros 3 títulos):")
        for i, titulo in enumerate(df_data_analyst['Job Title'].head(3)):
            print(f"  {i+1}. {titulo}")

    print(f"\n=== PROCESO COMPLETADO ===")
    print(f"Se han creado 4 archivos CSV:")
    print(f"1. puestos_qa_testing.csv")
    print(f"2. puestos_developer.csv")
    print(f"3. puestos_data_analyst.csv")
    print(f"4. puestos_consolidado_tres_perfiles.csv")

if __name__ == "__main__":
    extraer_puestos_por_perfil()