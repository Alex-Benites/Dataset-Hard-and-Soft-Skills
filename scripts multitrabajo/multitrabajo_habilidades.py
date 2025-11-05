import pandas as pd
import re

def extraer_habilidades_multitrabajos(descripcion, titulo):
    """
    Extrae habilidades técnicas (hard) y blandas (soft) de la descripción del trabajo de Multitrabajos
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
        'python': ['python', 'django', 'flask'],
        'php': ['php', 'laravel', 'yii', 'codeigniter'],
        'c#': ['c#', '.net', 'asp.net', 'net core'],
        'c++': ['c++', 'c ', 'cpp'],
        'html/css': ['html', 'css', 'html5', 'css3', 'bootstrap'],
        'sql': ['sql', 'mysql', 'postgresql', 'oracle', 'sql server'],
        'react': ['react', 'reactjs', 'angular', 'vue'],
        'next.js': ['next.js', 'nextjs'],
        'quarkus': ['quarkus'],
        'visual basic': ['visual basic.net', 'vb.net'],
        'r': ['lenguaje r', ' r,', 'r '],
        'kotlin': ['kotlin']
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
        'excel': ['excel', 'microsoft office'],
        'power bi': ['power bi', 'powerbi', 'tableau'],
        'oracle fusion': ['oracle fusion', 'otbi'],
        'microservicios': ['microservicios', 'microservices'],
        'restful apis': ['rest', 'restful', 'api', 'apis', 'web services'],
        'scrum': ['scrum', 'agile', 'ágil', 'kanban'],
        'devops': ['devops'],
        'ci/cd': ['ci/cd', 'continuous integration', 'continuous deployment'],
        'visual studio': ['visual studio'],
        'sql server': ['sql server', 'microsoft sql server'],
        'crm': ['crm'],
        'erp': ['erp'],
        'sap': ['sap'],
        'microsoft dynamics': ['dynamics 365', 'microsoft dynamics'],
        'sharepoint': ['sharepoint'],
        'teams': ['microsoft teams', 'teams'],
        'word': ['microsoft word', 'word'],
        'powerpoint': ['powerpoint'],
        'autocad': ['autocad'],
        'bim': ['bim'],
        'mac': ['macos', 'mac os'],
        'apple': ['apple', 'ios'],
        'windows': ['windows'],
        'linux': ['linux', 'unix'],
        'machine learning': ['machine learning', 'ml', 'ai', 'artificial intelligence'],
        'poo': ['poo', 'programación orientada a objetos'],
        'mvc': ['mvc', 'model view controller'],
        'asp.net': ['asp.net'],
        'angular': ['angular'],
        'vue.js': ['vue.js', 'vuejs']
    }

    for tech, keywords in tecnologias.items():
        if any(keyword in descripcion for keyword in keywords):
            hard_skills.append(tech)

    # Habilidades específicas por área
    if 'qa' in titulo or 'quality' in titulo or 'calidad' in titulo or 'supervisor qa' in titulo:
        qa_skills = ['pruebas manuales', 'pruebas automatizadas', 'testing', 'casos de prueba', 'control de calidad', 'inspección', 'auditoría']
        for skill in qa_skills:
            if any(word in descripcion for word in skill.split()):
                hard_skills.append(skill)

    if 'analista' in titulo and 'datos' in titulo:
        data_skills = ['análisis de datos', 'estadística', 'reporting', 'dashboards', 'kpis', 'métricas', 'business intelligence']
        for skill in data_skills:
            if skill in descripcion or any(word in descripcion for word in skill.split()):
                hard_skills.append(skill)

    if 'desarrollador' in titulo or 'programador' in titulo or 'software engineer' in titulo:
        dev_skills = ['desarrollo web', 'desarrollo móvil', 'programación', 'desarrollo de software', 'desarrollo de aplicaciones']
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
        'responsabilidad': ['responsable', 'responsabilidad', 'compromiso'],
        'planificación': ['planificación', 'planning', 'organización'],
        'negociación': ['negociación', 'negotiation'],
        'tolerancia a la presión': ['tolerancia a la presión', 'pressure', 'estrés'],
        'servicio al cliente': ['servicio al cliente', 'customer service', 'atención al cliente']
    }

    for skill, keywords in soft_keywords.items():
        if any(keyword in descripcion for keyword in keywords):
            soft_skills.append(skill)

    # Agregar algunas habilidades blandas comunes por área si no se detectaron muchas
    if len(soft_skills) < 3:
        if 'desarrollador' in titulo or 'programador' in titulo or 'software engineer' in titulo:
            soft_skills.extend(['trabajo en equipo', 'resolución de problemas', 'aprendizaje continuo'])
        elif 'qa' in titulo or 'supervisor' in titulo or 'calidad' in titulo:
            soft_skills.extend(['atención al detalle', 'comunicación', 'responsabilidad'])
        elif 'analista' in titulo:
            soft_skills.extend(['pensamiento crítico', 'atención al detalle', 'comunicación'])
        elif 'líder' in titulo or 'cto' in titulo or 'jefe' in titulo:
            soft_skills.extend(['liderazgo', 'comunicación', 'gestión del tiempo'])

    # Eliminar duplicados manteniendo el orden
    hard_skills = list(dict.fromkeys(hard_skills))
    soft_skills = list(dict.fromkeys(soft_skills))

    return hard_skills, soft_skills

def procesar_habilidades_multitrabajos():
    """
    Procesa el CSV de Multitrabajos agregando columnas de habilidades y eliminando descripcion y categoria
    """
    print("🚀 PROCESANDO HABILIDADES EN CSV DE MULTITRABAJOS")
    print("="*60)

    # Leer el CSV
    try:
        df = pd.read_csv('multitrabajos_jobs.csv')
        print(f"✅ Archivo leído exitosamente: {len(df)} registros")
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'multitrabajos_jobs.csv'")
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
        hard, soft = extraer_habilidades_multitrabajos(row['descripcion'], row['titulo'])

        # Convertir listas a strings separados por comas
        hard_str = ', '.join(hard) if hard else 'No especificado'
        soft_str = ', '.join(soft) if soft else 'No especificado'

        habilidades_hard.append(hard_str)
        habilidades_soft.append(soft_str)

        if (index + 1) % 5 == 0:
            print(f"   Procesados: {index + 1}/{len(df)} empleos")

    # Agregar las nuevas columnas al DataFrame
    df['habilidades_hard'] = habilidades_hard
    df['habilidades_soft'] = habilidades_soft

    # CAMBIO: Eliminar las columnas 'descripcion' y 'categoria'
    columnas_a_eliminar = ['descripcion', 'categoria']
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
    output_filename = 'multitrabajos_jobs_con_habilidades.csv'
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
    df_resultado = procesar_habilidades_multitrabajos()

    print("\n" + "="*60)
    print("✅ PROCESO COMPLETADO")
    print("="*60)