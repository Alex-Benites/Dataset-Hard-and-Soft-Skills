import pandas as pd
import re

def extraer_habilidades_opcion_empleo(descripcion, titulo):
    """
    Extrae habilidades técnicas (hard) y blandas (soft) de la descripción del trabajo de OpciónEmpleo
    """
    if pd.isna(descripcion):
        descripcion = ""

    descripcion = descripcion.lower()
    titulo = titulo.lower() if pd.notna(titulo) else ""

    # HABILIDADES TÉCNICAS (HARD SKILLS)
    hard_skills = []

    # Lenguajes de programación
    lenguajes = {
        'java': ['java', 'spring boot', 'spring', 'hibernate'],
        'javascript': ['javascript', 'js', 'typescript', 'node.js', 'nodejs'],
        'python': ['python', 'django', 'flask', 'pandas', 'numpy'],
        'php': ['php', 'laravel', 'yii', 'codeigniter'],
        'c#': ['c#', '.net', 'asp.net', 'net core'],
        'c++': ['c++', 'c ', 'cpp'],
        'html/css': ['html', 'css', 'html5', 'css3', 'bootstrap'],
        'sql': ['sql', 'mysql', 'postgresql', 'oracle', 'sql server'],
        'react': ['react', 'reactjs', 'angular', 'vue'],
        'next.js': ['next.js', 'nextjs'],
        'quarkus': ['quarkus'],
        'visual basic': ['visual basic', 'vb.net'],
        'kotlin': ['kotlin'],
        'swift': ['swift'],
        'flutter': ['flutter'],
        'react native': ['react native']
    }

    for skill, keywords in lenguajes.items():
        if any(keyword in descripcion for keyword in keywords):
            hard_skills.append(skill)

    # Tecnologías y herramientas
    tecnologias = {
        'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda'],
        'azure': ['azure', 'microsoft azure'],
        'gcp': ['gcp', 'google cloud'],
        'kubernetes': ['kubernetes', 'k8s'],
        'docker': ['docker', 'contenedores'],
        'jenkins': ['jenkins'],
        'git': ['git', 'github', 'gitlab'],
        'jira': ['jira'],
        'confluence': ['confluence'],
        'selenium': ['selenium'],
        'cypress': ['cypress'],
        'appium': ['appium'],
        'jmeter': ['jmeter'],
        'postman': ['postman'],
        'soapui': ['soapui', 'soap ui'],
        'excel': ['excel', 'microsoft office'],
        'power bi': ['power bi', 'powerbi', 'tableau'],
        'oracle fusion': ['oracle fusion', 'otbi'],
        'dynamics 365': ['dynamics 365', 'microsoft dynamics'],
        'microservicios': ['microservicios', 'microservices'],
        'restful apis': ['rest', 'restful', 'api', 'apis', 'web services'],
        'scrum': ['scrum', 'agile', 'ágil', 'kanban'],
        'devops': ['devops'],
        'ci/cd': ['ci/cd', 'continuous integration', 'continuous deployment'],
        'erp': ['erp'],
        'crm': ['crm'],
        'sharepoint': ['sharepoint'],
        'power platform': ['power platform', 'power apps', 'power automate'],
        'figma': ['figma'],
        'adobe xd': ['adobe xd'],
        'sketch': ['sketch'],
        'miro': ['miro'],
        'notion': ['notion'],
        'linux': ['linux', 'unix'],
        'windows': ['windows'],
        'macos': ['macos', 'mac os'],
        'discord': ['discord'],
        'teams': ['microsoft teams', 'teams'],
        'zoom': ['zoom'],
        'machine learning': ['machine learning', 'ml', 'ai', 'artificial intelligence'],
        'business intelligence': ['business intelligence', 'bi'],
        'data analysis': ['data analysis', 'análisis de datos'],
        'ux/ui': ['ux/ui', 'user experience', 'user interface']
    }

    for tech, keywords in tecnologias.items():
        if any(keyword in descripcion for keyword in keywords):
            hard_skills.append(tech)

    # Habilidades específicas por área
    if 'qa' in titulo or 'quality' in titulo or 'calidad' in titulo or 'tester' in titulo:
        qa_skills = ['pruebas manuales', 'pruebas automatizadas', 'testing', 'casos de prueba', 'control de calidad', 'test automation']
        for skill in qa_skills:
            if any(word in descripcion for word in skill.split()):
                hard_skills.append(skill)

    if 'analista' in titulo and 'datos' in titulo:
        data_skills = ['análisis de datos', 'estadística', 'reporting', 'dashboards', 'kpis', 'métricas']
        for skill in data_skills:
            if skill in descripcion or any(word in descripcion for word in skill.split()):
                hard_skills.append(skill)

    if 'desarrollador' in titulo or 'developer' in titulo or 'programador' in titulo:
        dev_skills = ['desarrollo web', 'desarrollo móvil', 'programación', 'desarrollo de software']
        for skill in dev_skills:
            if any(word in descripcion for word in skill.split()):
                hard_skills.append(skill)

    # HABILIDADES BLANDAS (SOFT SKILLS)
    soft_skills = []

    soft_keywords = {
        'trabajo en equipo': ['equipo', 'colabora', 'colaboración', 'team', 'teamwork'],
        'comunicación': ['comunicación', 'comunicar', 'presentar', 'communication'],
        'liderazgo': ['liderazgo', 'liderar', 'líder', 'gestión de equipos', 'leadership'],
        'resolución de problemas': ['resolución de problemas', 'problem solving', 'analítico', 'análisis'],
        'adaptabilidad': ['adaptab', 'flexible', 'cambio', 'adaptability'],
        'orientación a resultados': ['resultados', 'objetivos', 'metas', 'goals'],
        'aprendizaje continuo': ['aprender', 'aprendizaje', 'capacitación', 'mejora continua', 'learning'],
        'atención al detalle': ['detalle', 'precisión', 'calidad', 'attention to detail'],
        'proactividad': ['proactiv', 'iniciativa', 'autónomo', 'proactive'],
        'gestión del tiempo': ['tiempo', 'plazos', 'organización', 'time management'],
        'creatividad': ['creativ', 'innovador', 'innovación', 'creative'],
        'pensamiento crítico': ['crítico', 'evaluar', 'toma de decisiones', 'critical thinking'],
        'inglés avanzado': ['inglés', 'english', 'advanced english', 'fluent english'],
        'mentoría': ['mentoring', 'mentoría', 'coaching'],
        'multitarea': ['multitask', 'multitarea', 'multiple tasks'],
        'negociación': ['negociación', 'negotiation'],
        'planificación': ['planificación', 'planning'],
        'servicio al cliente': ['servicio al cliente', 'customer service', 'atención al cliente'],
        'gestión de proyectos': ['gestión de proyectos', 'project management'],
        'responsabilidad': ['responsable', 'responsabilidad', 'compromiso']
    }

    for skill, keywords in soft_keywords.items():
        if any(keyword in descripcion for keyword in keywords):
            soft_skills.append(skill)

    # Agregar algunas habilidades blandas comunes por área si no se detectaron muchas
    if len(soft_skills) < 3:
        if 'desarrollador' in titulo or 'developer' in titulo or 'programador' in titulo:
            soft_skills.extend(['trabajo en equipo', 'resolución de problemas', 'aprendizaje continuo'])
        elif 'qa' in titulo or 'tester' in titulo:
            soft_skills.extend(['atención al detalle', 'comunicación', 'responsabilidad'])
        elif 'analista' in titulo:
            soft_skills.extend(['pensamiento crítico', 'atención al detalle', 'comunicación'])
        elif 'ux' in titulo or 'ui' in titulo or 'diseño' in titulo:
            soft_skills.extend(['creatividad', 'comunicación', 'trabajo en equipo'])

    # Eliminar duplicados manteniendo el orden
    hard_skills = list(dict.fromkeys(hard_skills))
    soft_skills = list(dict.fromkeys(soft_skills))

    return hard_skills, soft_skills

def procesar_habilidades_opcion_empleo():
    """
    Procesa el CSV de OpciónEmpleo agregando columnas de habilidades y eliminando descripcion y tipo_contrato
    """
    print("🚀 PROCESANDO HABILIDADES EN CSV DE OPCIONEMPLEO")
    print("="*60)

    # Leer el CSV
    try:
        df = pd.read_csv('opcionEmpleo_jobs.csv')
        print(f"✅ Archivo leído exitosamente: {len(df)} registros")
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'opcionEmpleo_jobs.csv'")
        return

    print("\nColumnas encontradas:", df.columns.tolist())

    # Verificar que existan las columnas necesarias
    if 'descripcion' not in df.columns or 'titulo' not in df.columns:
        print("❌ Error: Faltan las columnas 'descripcion' o 'titulo'")
        return

    print(f"\n📊 Procesando {len(df)} empleos...")

    # Listas para almacenar las habilidades
    habilidades_hard = []
    habilidades_soft = []

    # Procesar cada registro
    for index, row in df.iterrows():
        hard, soft = extraer_habilidades_opcion_empleo(row['descripcion'], row['titulo'])

        # Convertir listas a strings separados por comas
        hard_str = ', '.join(hard) if hard else 'No especificado'
        soft_str = ', '.join(soft) if soft else 'No especificado'

        habilidades_hard.append(hard_str)
        habilidades_soft.append(soft_str)

        if (index + 1) % 20 == 0:
            print(f"   Procesados: {index + 1}/{len(df)} empleos")

    # Agregar las nuevas columnas al DataFrame
    df['habilidades_hard'] = habilidades_hard
    df['habilidades_soft'] = habilidades_soft

    # CAMBIO: Eliminar las columnas 'descripcion' y 'tipo_contrato'
    columnas_a_eliminar = ['descripcion', 'tipo_contrato']
    columnas_eliminadas = []

    for col in columnas_a_eliminar:
        if col in df.columns:
            df = df.drop(columns=[col])
            columnas_eliminadas.append(col)
            print(f"   ✅ Columna '{col}' eliminada")

    if columnas_eliminadas:
        print(f"📝 Columnas eliminadas: {', '.join(columnas_eliminadas)}")

    # Reordenar columnas para poner las habilidades al final
    columnas = [col for col in df.columns if col not in ['habilidades_hard', 'habilidades_soft']]
    columnas.extend(['habilidades_hard', 'habilidades_soft'])
    df = df[columnas]

    # Guardar el archivo actualizado
    output_filename = 'opcionEmpleo_jobs_con_habilidades.csv'
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"\n✅ Archivo guardado exitosamente: {output_filename}")
    print(f"📊 Total de registros: {len(df)}")
    print(f"📋 Columnas finales: {len(df.columns)}")
    print(f"📋 Columnas actuales: {df.columns.tolist()}")

    # Mostrar estadísticas
    print("\n📊 ESTADÍSTICAS DE HABILIDADES:")
    print(f"   Empleos con habilidades hard: {len([h for h in habilidades_hard if h != 'No especificado'])}")
    print(f"   Empleos con habilidades soft: {len([h for h in habilidades_soft if h != 'No especificado'])}")

    # Mostrar algunas muestras
    print("\n📋 MUESTRA DE RESULTADOS:")
    for i in range(min(3, len(df))):
        print(f"\n--- Empleo {i+1}: {df.iloc[i]['titulo']} ---")
        print(f"Area: {df.iloc[i]['Area']}")
        print(f"Habilidades Hard: {df.iloc[i]['habilidades_hard']}")
        print(f"Habilidades Soft: {df.iloc[i]['habilidades_soft']}")

    # Mostrar estadísticas por área
    print("\n📊 ESTADÍSTICAS POR ÁREA:")
    if 'Area' in df.columns:
        for area in df['Area'].unique():
            area_data = df[df['Area'] == area]
            hard_con_datos = len([h for h in area_data['habilidades_hard'] if h != 'No especificado'])
            soft_con_datos = len([h for h in area_data['habilidades_soft'] if h != 'No especificado'])
            print(f"   {area}: {len(area_data)} empleos - Hard: {hard_con_datos}, Soft: {soft_con_datos}")

    return df

if __name__ == "__main__":
    df_resultado = procesar_habilidades_opcion_empleo()

    print("\n" + "="*60)
    print("✅ PROCESO COMPLETADO")
    print("="*60)