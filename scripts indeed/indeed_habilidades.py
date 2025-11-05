import pandas as pd
import re

def extraer_habilidades_indeed(descripcion, titulo):
    """
    Extrae habilidades técnicas (hard) y blandas (soft) de la descripción del trabajo de Indeed
    """
    if pd.isna(descripcion):
        descripcion = ""

    descripcion = descripcion.lower()
    titulo = titulo.lower() if pd.notna(titulo) else ""

    # HABILIDADES TÉCNICAS (HARD SKILLS)
    hard_skills = []

    # Lenguajes de programación
    lenguajes = {
        'java': ['java', 'spring boot', 'spring', 'hibernate', 'quarkus'],
        'javascript': ['javascript', 'js', 'typescript', 'node.js', 'nodejs', 'react', 'angular', 'vue'],
        'python': ['python', 'django', 'flask', 'pandas', 'numpy'],
        'php': ['php', 'laravel', 'yii', 'codeigniter'],
        'c#': ['c#', '.net', 'asp.net', 'net core'],
        'c++': ['c++', 'c ', 'cpp'],
        'html/css': ['html', 'css', 'html5', 'css3', 'bootstrap'],
        'sql': ['sql', 'mysql', 'postgresql', 'oracle', 'sql server', 'transact-sql'],
        'r': ['lenguajes de progrmación: r', ' r,', 'r ', 'rstudio'],
        'kotlin': ['kotlin'],
        'swift': ['swift'],
        'go': ['golang', ' go '],
        'scala': ['scala'],
        'next.js': ['next.js', 'nextjs'],
        'nuxt.js': ['nuxt.js', 'nuxtjs']
    }

    for skill, keywords in lenguajes.items():
        if any(keyword in descripcion for keyword in keywords):
            hard_skills.append(skill)

    # Tecnologías y herramientas
    tecnologias = {
        'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda'],
        'azure': ['azure', 'microsoft azure', 'azure devops'],
        'gcp': ['gcp', 'google cloud'],
        'kubernetes': ['kubernetes', 'k8s'],
        'docker': ['docker', 'contenedores', 'containers'],
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
        'microservicios': ['microservicios', 'microservices'],
        'restful apis': ['rest', 'restful', 'api', 'apis', 'web services'],
        'scrum': ['scrum', 'agile', 'ágil', 'kanban'],
        'ci/cd': ['ci/cd', 'continuous integration', 'continuous deployment'],
        'devops': ['devops'],
        'kafka': ['kafka'],
        'rabbitmq': ['rabbitmq'],
        'redis': ['redis'],
        'mongodb': ['mongodb', 'nosql'],
        'elasticsearch': ['elasticsearch'],
        'machine learning': ['machine learning', 'ml', 'artificial intelligence', 'ai'],
        'powerpoint': ['powerpoint', 'presentaciones'],
        'word': ['word'],
        'teams': ['teams', 'microsoft teams'],
        'sharepoint': ['sharepoint'],
        'figma': ['figma'],
        'sketch': ['sketch'],
        'photoshop': ['photoshop'],
        'linux': ['linux', 'unix'],
        'windows': ['windows'],
        'macos': ['macos', 'mac os'],
        'salesforce': ['salesforce'],
        'dynamics 365': ['dynamics 365', 'microsoft dynamics'],
        'sap': ['sap'],
        'erp': ['erp'],
        'crm': ['crm'],
        'bi': ['business intelligence', 'inteligencia de negocios']
    }

    for tech, keywords in tecnologias.items():
        if any(keyword in descripcion for keyword in keywords):
            hard_skills.append(tech)

    # Habilidades específicas por área
    if 'qa' in titulo or 'quality' in titulo or 'calidad' in titulo or 'tester' in titulo or 'testing' in titulo:
        qa_skills = ['pruebas manuales', 'pruebas automatizadas', 'testing', 'casos de prueba', 'test automation']
        for skill in qa_skills:
            if any(word in descripcion for word in skill.split()):
                hard_skills.append(skill)

    if 'analista' in titulo and 'datos' in titulo:
        data_skills = ['análisis de datos', 'estadística', 'reporting', 'data analysis', 'dashboards']
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
        'resolución de problemas': ['resolución de problemas', 'problem solving', 'analítico', 'análisis', 'troubleshooting'],
        'adaptabilidad': ['adaptab', 'flexible', 'cambio', 'adaptability'],
        'orientación a resultados': ['resultados', 'objetivos', 'metas', 'goals'],
        'aprendizaje continuo': ['aprender', 'aprendizaje', 'capacitación', 'mejora continua', 'learning'],
        'atención al detalle': ['detalle', 'precisión', 'calidad', 'attention to detail'],
        'proactividad': ['proactiv', 'iniciativa', 'autónomo', 'proactive'],
        'gestión del tiempo': ['tiempo', 'plazos', 'organización', 'time management'],
        'creatividad': ['creativ', 'innovador', 'innovación', 'creative'],
        'pensamiento crítico': ['crítico', 'evaluar', 'toma de decisiones', 'critical thinking'],
        'inglés avanzado': ['inglés', 'english', 'advanced english', 'fluent english', 'intermedio'],
        'mentoría': ['mentoring', 'mentoría', 'coaching'],
        'multitarea': ['multitask', 'multitarea', 'multiple tasks'],
        'negociación': ['negociación', 'negotiation'],
        'presentaciones': ['presentaciones', 'presentations'],
        'servicio al cliente': ['servicio al cliente', 'customer service', 'atención al cliente'],
        'gestión de proyectos': ['gestión de proyectos', 'project management'],
        'planificación': ['planificación', 'planning']
    }

    for skill, keywords in soft_keywords.items():
        if any(keyword in descripcion for keyword in keywords):
            soft_skills.append(skill)

    # Agregar algunas habilidades blandas comunes por área si no se detectaron muchas
    if len(soft_skills) < 3:
        if 'desarrollador' in titulo or 'developer' in titulo or 'programador' in titulo:
            soft_skills.extend(['trabajo en equipo', 'resolución de problemas', 'aprendizaje continuo'])
        elif 'qa' in titulo or 'tester' in titulo:
            soft_skills.extend(['atención al detalle', 'comunicación', 'pensamiento crítico'])
        elif 'analista' in titulo:
            soft_skills.extend(['pensamiento crítico', 'atención al detalle', 'comunicación'])
        elif 'tech lead' in titulo or 'líder' in titulo:
            soft_skills.extend(['liderazgo', 'comunicación', 'mentoría'])

    # Eliminar duplicados manteniendo el orden
    hard_skills = list(dict.fromkeys(hard_skills))
    soft_skills = list(dict.fromkeys(soft_skills))

    return hard_skills, soft_skills

def procesar_habilidades_indeed():
    """
    Procesa el CSV de Indeed agregando columnas de habilidades y eliminando descripcion y tipo_contrato
    """
    print("🚀 PROCESANDO HABILIDADES EN CSV DE INDEED")
    print("="*60)

    # Leer el CSV
    try:
        df = pd.read_csv('indeed_jobs.csv')
        print(f"✅ Archivo leído exitosamente: {len(df)} registros")
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'indeed_jobs.csv'")
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
        hard, soft = extraer_habilidades_indeed(row['descripcion'], row['titulo'])

        # Convertir listas a strings separados por comas
        hard_str = ', '.join(hard) if hard else 'No especificado'
        soft_str = ', '.join(soft) if soft else 'No especificado'

        habilidades_hard.append(hard_str)
        habilidades_soft.append(soft_str)

        if (index + 1) % 10 == 0:
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
    output_filename = 'indeed_jobs_con_habilidades.csv'
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
    df_resultado = procesar_habilidades_indeed()

    print("\n" + "="*60)
    print("✅ PROCESO COMPLETADO")
    print("="*60)