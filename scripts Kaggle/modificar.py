import pandas as pd
import re
from deep_translator import GoogleTranslator

def traducir_habilidades_hibrido():
    """
    Traduce usando diccionario primero, luego librería para lo que falta
    """

    print("Cargando dataset...")
    df = pd.read_csv('dataset_kaggle_final.csv')
    print(f"Dataset cargado: {len(df)} registros")

    # Diccionario para términos CRÍTICOS (control total)
    traducciones_soft = {
        'Communication': 'Comunicación',
        'Teamwork': 'Trabajo en equipo',
        'Leadership': 'Liderazgo',
        'Management': 'Gestión',
        'Problem Solving': 'Resolución de problemas',
        'Analytical': 'Analítico',
        'Critical Thinking': 'Pensamiento crítico',
        'Adaptability': 'Adaptabilidad',
        'Flexibility': 'Flexibilidad',
        'Learning': 'Aprendizaje',
        'Organization': 'Organización',
        'Time Management': 'Gestión del tiempo',
        'Planning': 'Planificación',
        'Multitasking': 'Multitarea',
        'Proactive': 'Proactivo',
        'Initiative': 'Iniciativa',
        'Creativity': 'Creatividad',
        'Innovation': 'Innovación',
        'Attention To Detail': 'Atención al detalle',
        'Accuracy': 'Precisión',
        'Quality Focus': 'Enfoque en calidad',
        'Presentation': 'Presentación',
        'Writing': 'Escritura',
        'Verbal': 'Verbal',
        'Listening': 'Escucha',
        'Coaching': 'Coaching',
        'Mentoring': 'Mentoría',
        'Delegation': 'Delegación',
        'Collaboration': 'Colaboración',
        'Interpersonal': 'Interpersonal',
        'Networking': 'Networking',
        'Troubleshooting': 'Resolución de problemas técnicos',
        'Debugging': 'Depuración',
        'Curiosity': 'Curiosidad',
        'Continuous Learning': 'Aprendizaje continuo',
        'Self-Motivated': 'Auto-motivado',
        'Prioritization': 'Priorización',
        'Project Management': 'Gestión de proyectos',
        'Task Management': 'Gestión de tareas',
        'Quality Assurance': 'Aseguramiento de calidad',
        'Quality Control': 'Control de calidad',
        'Meticulous': 'Meticuloso',
        'Thorough': 'Minucioso',
        'Detail-Oriented': 'Orientado al detalle',
        'Cross-Functional': 'Multi-funcional',
        'Root Cause Analysis': 'Análisis de causa raíz'
    }

    # Inicializar traductor (solo para lo que no está en diccionario)
    translator = GoogleTranslator(source='en', target='es')

    # Estadísticas
    stats = {
        'diccionario': 0,
        'traductor': 0,
        'no_traducido': 0
    }

    def traducir_soft_hibrido(texto):
        """Traduce usando diccionario primero, luego Google Translator"""
        if pd.isna(texto) or texto == 'No especificado' or texto == '':
            return texto

        texto_original = str(texto)
        texto_traducido = texto_original

        # PASO 1: Aplicar diccionario (ordenado por longitud)
        items_ordenados = sorted(traducciones_soft.items(), key=lambda x: len(x[0]), reverse=True)

        for ingles, espanol in items_ordenados:
            patron = r'\b' + re.escape(ingles) + r'\b'
            texto_traducido = re.sub(patron, espanol, texto_traducido, flags=re.IGNORECASE)

        # PASO 2: Si quedaron palabras en inglés, traducir con Google
        # Detectar si todavía hay inglés (palabras comunes en inglés)
        palabras_ingles = ['and', 'or', 'with', 'for', 'the', 'in', 'of', 'to']
        tiene_ingles = any(palabra in texto_traducido.lower() for palabra in palabras_ingles)

        if tiene_ingles or texto_traducido == texto_original:
            try:
                # Separar por comas y traducir cada habilidad individualmente
                habilidades = [h.strip() for h in texto_traducido.split(',')]
                habilidades_traducidas = []

                for hab in habilidades:
                    # Si ya está en español o es muy corta, mantener
                    if any(esp in hab for esp in traducciones_soft.values()) or len(hab) < 3:
                        habilidades_traducidas.append(hab)
                        stats['diccionario'] += 1
                    else:
                        # Traducir con Google
                        try:
                            hab_traducida = translator.translate(hab)
                            habilidades_traducidas.append(hab_traducida)
                            stats['traductor'] += 1
                        except:
                            habilidades_traducidas.append(hab)
                            stats['no_traducido'] += 1

                texto_traducido = ', '.join(habilidades_traducidas)
            except:
                stats['no_traducido'] += 1
        else:
            stats['diccionario'] += 1

        return texto_traducido

    print("\nTraduciendo habilidades soft (método híbrido)...")

    # Mostrar muestra antes
    print(f"\n=== ANTES (muestra) ===")
    for i in range(5):
        if df.iloc[i]['habilidades_soft'] != 'No especificado':
            print(f"{i+1}. {df.iloc[i]['habilidades_soft'][:80]}...")

    # Aplicar traducción
    df['habilidades_soft'] = df['habilidades_soft'].apply(traducir_soft_hibrido)

    # Mostrar muestra después
    print(f"\n=== DESPUÉS (muestra) ===")
    for i in range(5):
        if df.iloc[i]['habilidades_soft'] != 'No especificado':
            print(f"{i+1}. {df.iloc[i]['habilidades_soft'][:80]}...")

    # Mostrar estadísticas
    print(f"\n=== ESTADÍSTICAS DE TRADUCCIÓN ===")
    print(f"Traducidas por diccionario: {stats['diccionario']}")
    print(f"Traducidas por Google: {stats['traductor']}")
    print(f"No traducidas: {stats['no_traducido']}")

    # Guardar
    df.to_csv('dataset_kaggle_final.csv', index=False)
    print(f"\n✓ Dataset guardado: dataset_kaggle_final.csv")
    print(f"✓ Habilidades soft traducidas correctamente")

def analizar_eliminacion_no_especificado():
    """
    Analiza cuántos registros quedarían si eliminamos los 'No especificado'
    """

    print("Cargando dataset...")
    df = pd.read_csv('dataset_kaggle_final.csv')
    print(f"Dataset original: {len(df):,} registros")

    print("\n" + "="*80)
    print("ANÁLISIS DE REGISTROS CON 'NO ESPECIFICADO'")
    print("="*80)

    # Contar registros con "No especificado"
    hard_no_especificado = len(df[df['habilidades_hard'] == 'No especificado'])
    soft_no_especificado = len(df[df['habilidades_soft'] == 'No especificado'])
    ambos_no_especificado = len(df[(df['habilidades_hard'] == 'No especificado') |
                                    (df['habilidades_soft'] == 'No especificado')])

    print(f"\n📊 SITUACIÓN ACTUAL:")
    print(f"  Registros con habilidades_hard 'No especificado': {hard_no_especificado:,} ({hard_no_especificado/len(df)*100:.1f}%)")
    print(f"  Registros con habilidades_soft 'No especificado': {soft_no_especificado:,} ({soft_no_especificado/len(df)*100:.1f}%)")
    print(f"  Registros con AL MENOS UNA 'No especificado': {ambos_no_especificado:,} ({ambos_no_especificado/len(df)*100:.1f}%)")

    # ESCENARIO 1: Eliminar si AMBAS son "No especificado"
    df_filtrado_ambas = df[~((df['habilidades_hard'] == 'No especificado') &
                             (df['habilidades_soft'] == 'No especificado'))]

    print(f"\n🔍 ESCENARIO 1: Eliminar solo si AMBAS son 'No especificado'")
    print(f"  Registros que se eliminarían: {len(df) - len(df_filtrado_ambas):,}")
    print(f"  ✅ Registros restantes: {len(df_filtrado_ambas):,} ({len(df_filtrado_ambas)/len(df)*100:.1f}%)")

    # ESCENARIO 2: Eliminar si CUALQUIERA es "No especificado"
    df_filtrado_cualquiera = df[(df['habilidades_hard'] != 'No especificado') &
                                (df['habilidades_soft'] != 'No especificado')]

    print(f"\n🔍 ESCENARIO 2: Eliminar si CUALQUIERA es 'No especificado'")
    print(f"  Registros que se eliminarían: {len(df) - len(df_filtrado_cualquiera):,}")
    print(f"  ✅ Registros restantes: {len(df_filtrado_cualquiera):,} ({len(df_filtrado_cualquiera)/len(df)*100:.1f}%)")

    # ESCENARIO 3: Eliminar solo si habilidades_hard es "No especificado"
    df_filtrado_hard = df[df['habilidades_hard'] != 'No especificado']

    print(f"\n🔍 ESCENARIO 3: Eliminar solo si habilidades_hard es 'No especificado'")
    print(f"  Registros que se eliminarían: {len(df) - len(df_filtrado_hard):,}")
    print(f"  ✅ Registros restantes: {len(df_filtrado_hard):,} ({len(df_filtrado_hard)/len(df)*100:.1f}%)")

    # ESCENARIO 4: Eliminar solo si habilidades_soft es "No especificado"
    df_filtrado_soft = df[df['habilidades_soft'] != 'No especificado']

    print(f"\n🔍 ESCENARIO 4: Eliminar solo si habilidades_soft es 'No especificado'")
    print(f"  Registros que se eliminarían: {len(df) - len(df_filtrado_soft):,}")
    print(f"  ✅ Registros restantes: {len(df_filtrado_soft):,} ({len(df_filtrado_soft)/len(df)*100:.1f}%)")

    # Distribución por perfil en ESCENARIO 2 (el más restrictivo)
    print(f"\n📈 DISTRIBUCIÓN POR PERFIL (Escenario 2 - Ambas especificadas):")
    print(f"\n{'Perfil':<30} {'Original':<15} {'Filtrado':<15} {'% Conservado':<15}")
    print("-" * 75)

    for area in df['Area'].unique():
        original = len(df[df['Area'] == area])
        filtrado = len(df_filtrado_cualquiera[df_filtrado_cualquiera['Area'] == area])
        porcentaje = (filtrado / original) * 100 if original > 0 else 0

        print(f"{area:<30} {original:>10,} {filtrado:>14,} {porcentaje:>13.1f}%")

    # RECOMENDACIÓN
    print("\n" + "="*80)
    print("💡 RECOMENDACIÓN")
    print("="*80)
    print(f"""
    Para tu investigación, el ESCENARIO 2 es el más recomendado:

    ✅ Mantienes: {len(df_filtrado_cualquiera):,} registros ({len(df_filtrado_cualquiera)/len(df)*100:.1f}% del total)
    ✅ Eliminas: {len(df) - len(df_filtrado_cualquiera):,} registros con datos incompletos
    ✅ Garantizas: Todos los registros tienen AMBAS habilidades especificadas

    Esto te da un dataset de ALTA CALIDAD para análisis de correlación
    entre habilidades hard y soft.
    """)

    return df_filtrado_cualquiera

def eliminar_no_especificado():
    """
    Elimina registros con 'No especificado' y guarda el dataset limpio
    """

    print("Cargando dataset...")
    df = pd.read_csv('dataset_kaggle_final.csv')
    print(f"Dataset original: {len(df):,} registros")

    # Eliminar registros donde CUALQUIERA de las dos columnas sea "No especificado"
    df_limpio = df[(df['habilidades_hard'] != 'No especificado') &
                   (df['habilidades_soft'] != 'No especificado')]

    print(f"\nRegistros eliminados: {len(df) - len(df_limpio):,}")
    print(f"✅ Registros finales: {len(df_limpio):,}")

    # Guardar dataset limpio
    df_limpio.to_csv('dataset_kaggle_limpio.csv', index=False)
    print(f"\n✓ Dataset limpio guardado: dataset_kaggle_limpio.csv")

    return df_limpio

if __name__ == "__main__":
    # Primero analizar
    print("PASO 1: ANÁLISIS\n")
    df_analizado = analizar_eliminacion_no_especificado()

    # Preguntar si quiere eliminar
    print("\n" + "="*80)
    respuesta = input("\n¿Deseas eliminar los registros con 'No especificado' y guardar dataset limpio? (s/n): ")

    if respuesta.lower() == 's':
        print("\nPASO 2: ELIMINACIÓN Y GUARDADO\n")
        eliminar_no_especificado()
    else:
        print("\n❌ No se realizaron cambios. Dataset original intacto.")