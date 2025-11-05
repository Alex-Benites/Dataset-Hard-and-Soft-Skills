from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import random
import re

class MultitrabajosScraper:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]

    def iniciar_driver(self):
        """Configura Chrome con anti-detección"""
        chrome_options = Options()
        chrome_options.add_argument(f'user-agent={random.choice(self.user_agents)}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es', 'en']});
            '''
        })

        return driver

    def limpiar_texto(self, texto):
        """Limpia texto eliminando espacios extra y caracteres especiales"""
        if not texto:
            return None
        # Limpiar espacios múltiples y caracteres extraños
        texto_limpio = re.sub(r'\s+', ' ', texto).strip()
        return texto_limpio if texto_limpio else None

    def extraer_detalles_trabajo(self, driver, url, index):
        """Extrae detalles específicos del trabajo desde Multitrabajos"""
        try:
            print(f"\n{'='*60}")
            print(f"📋 TRABAJO {index}/6")  # CAMBIO 1: Actualizar cantidad
            print(f"{'='*60}")
            print(f"📄 URL: {url}")

            # Ir a la URL del trabajo
            driver.get(url)
            time.sleep(random.uniform(4, 8))  # Aumentar tiempo de espera

            # Verificar que la página cargó - SELECTOR CORREGIDO
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-ifAKCX, .sc-bmlaxJ, .container"))
                )
                print("   ✅ Página cargada correctamente")
            except TimeoutException:
                print("   ❌ Error: Timeout al cargar la página")
                return None

            datos = {'url': url, 'index': index}

            # 1. TÍTULO del trabajo - SELECTORES CORREGIDOS
            try:
                titulo_elem = driver.find_element(By.CSS_SELECTOR, "h1.sc-dedDZB")
                datos['titulo'] = self.limpiar_texto(titulo_elem.text)
                print(f"   ✓ Título: {datos['titulo']}")
            except:
                try:
                    titulo_elem = driver.find_element(By.CSS_SELECTOR, "h1")
                    datos['titulo'] = self.limpiar_texto(titulo_elem.text)
                    print(f"   ✓ Título: {datos['titulo']}")
                except:
                    datos['titulo'] = None
                    print("   ✗ Título no encontrado")

            # 2. EMPRESA - SELECTORES CORREGIDOS
            try:
                empresa_elem = driver.find_element(By.CSS_SELECTOR, ".sc-cnyaSH")
                datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                print(f"   ✓ Empresa: {datos['empresa']}")
            except:
                try:
                    empresa_elem = driver.find_element(By.CSS_SELECTOR, ".sc-kAPOMq p")
                    datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                    print(f"   ✓ Empresa: {datos['empresa']}")
                except:
                    try:
                        # Buscar por texto que contenga el nombre de la empresa
                        empresa_elem = driver.find_element(By.XPATH, "//p[contains(@class, 'sc-')]//text()[contains(., 'S.A.') or contains(., 'C.A.') or contains(., 'LTDA') or contains(., 'CIA')]/..")
                        datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                        print(f"   ✓ Empresa: {datos['empresa']}")
                    except:
                        datos['empresa'] = None
                        print("   ✗ Empresa no encontrada")

            # 3. UBICACIÓN - SELECTORES CORREGIDOS
            try:
                ubicacion_elem = driver.find_element(By.CSS_SELECTOR, "h2.sc-iXxCOI")
                datos['ubicacion'] = self.limpiar_texto(ubicacion_elem.text)
                print(f"   ✓ Ubicación: {datos['ubicacion']}")
            except:
                try:
                    ubicacion_elem = driver.find_element(By.CSS_SELECTOR, "h2.sc-cygeCC, h2.sc-frreHP")
                    datos['ubicacion'] = self.limpiar_texto(ubicacion_elem.text)
                    print(f"   ✓ Ubicación: {datos['ubicacion']}")
                except:
                    try:
                        # Buscar cualquier h2 que contenga texto con comas (formato ubicación)
                        ubicacion_elems = driver.find_elements(By.XPATH, "//h2[contains(text(), ',')]")
                        if ubicacion_elems:
                            datos['ubicacion'] = self.limpiar_texto(ubicacion_elems[0].text)
                            print(f"   ✓ Ubicación: {datos['ubicacion']}")
                        else:
                            datos['ubicacion'] = None
                    except:
                        datos['ubicacion'] = None
                        print("   ✗ Ubicación no encontrada")

            # 4. MODALIDAD, JORNADA, SALARIO y otros detalles - SELECTORES CORREGIDOS
            try:
                print(f"   🔍 Buscando detalles del trabajo...")

                # SELECTORES BASADOS EN EL HTML REAL
                contenedores_detalles = [
                    "ul.sc-iEEPnt",      # Del information.html
                    "ul.sc-SxrYz",       # Del description.html
                    "ul.sc-cjEZae",      # Alternativo
                    ".sc-EHOje ul",      # Contenedor general
                    "ul li"              # Fallback
                ]

                elementos_li = []
                detalles_container = None

                for selector in contenedores_detalles:
                    try:
                        detalles_container = driver.find_element(By.CSS_SELECTOR, selector)
                        elementos_li = detalles_container.find_elements(By.CSS_SELECTOR, "li")
                        if elementos_li:
                            print(f"   ✓ Encontrado contenedor: {selector} con {len(elementos_li)} elementos")
                            break
                    except:
                        continue

                if not elementos_li:
                    # Buscar elementos li directamente en toda la página
                    elementos_li = driver.find_elements(By.CSS_SELECTOR, "li")
                    print(f"   ⚠️  Buscando elementos li en toda la página: {len(elementos_li)} encontrados")

                datos['modalidad'] = None
                datos['jornada'] = None
                datos['categoria'] = None
                datos['seniority'] = None
                datos['vacantes'] = None
                datos['salario'] = None

                for li in elementos_li:
                    try:
                        texto = li.text.lower().strip()

                        if not texto:
                            continue

                        # Modalidad (presencial, remoto, híbrido)
                        if any(word in texto for word in ['presencial', 'remoto', 'híbrido', 'teletrabajo']) and not datos['modalidad']:
                            datos['modalidad'] = self.limpiar_texto(li.text)
                            print(f"   ✓ Modalidad: {datos['modalidad']}")

                        # Jornada (full-time, part-time, etc.)
                        elif any(word in texto for word in ['full-time', 'part-time', 'tiempo completo', 'tiempo parcial', 'indeterminado']) and not datos['jornada']:
                            datos['jornada'] = self.limpiar_texto(li.text)
                            print(f"   ✓ Jornada: {datos['jornada']}")

                        # Salario (buscar patrones de dinero)
                        elif any(pattern in texto for pattern in ['$', 'usd', 'dólares', 'por mes', 'salario']) and not datos['salario']:
                            datos['salario'] = self.limpiar_texto(li.text)
                            print(f"   ✓ Salario: {datos['salario']}")

                        # Categoría (programación, tecnología, etc.)
                        elif any(word in texto for word in ['programación', 'tecnología', 'sistemas', 'desarrollo', 'informática']) and not datos['categoria']:
                            datos['categoria'] = self.limpiar_texto(li.text)
                            print(f"   ✓ Categoría: {datos['categoria']}")

                        # Seniority (junior, senior, semi sr, etc.)
                        elif any(word in texto for word in ['junior', 'senior', 'semi sr', 'jr', 'sr', 'no especificado']) and not datos['seniority']:
                            datos['seniority'] = self.limpiar_texto(li.text)
                            print(f"   ✓ Seniority: {datos['seniority']}")

                        # Vacantes disponibles
                        elif 'vacante' in texto and not datos['vacantes']:
                            datos['vacantes'] = self.limpiar_texto(li.text)
                            print(f"   ✓ Vacantes: {datos['vacantes']}")

                    except Exception as e:
                        continue

                # Buscar salario en párrafos si no se encontró en li
                if not datos['salario']:
                    try:
                        salario_patterns = [
                            ".sc-gIDicD",      # Selector específico para salario
                            ".sc-laUcbe",      # Alternativo
                            "*[class*='salario']",  # Cualquier clase que contenga salario
                        ]

                        for pattern in salario_patterns:
                            try:
                                salario_elem = driver.find_element(By.CSS_SELECTOR, pattern)
                                if any(word in salario_elem.text.lower() for word in ['$', 'usd', 'por mes']):
                                    datos['salario'] = self.limpiar_texto(salario_elem.text)
                                    print(f"   ✓ Salario (específico): {datos['salario']}")
                                    break
                            except:
                                continue
                    except:
                        pass

            except Exception as e:
                print(f"   ⚠️  Error extrayendo detalles: {e}")

            # 5. DESCRIPCIÓN COMPLETA - SELECTORES CORREGIDOS
            try:
                descripcion_elem = driver.find_element(By.CSS_SELECTOR, ".sc-fhogAb")
                datos['descripcion'] = self.limpiar_texto(descripcion_elem.text)
                print(f"   ✓ Descripción: {len(datos['descripcion'])} caracteres")
            except:
                try:
                    # Selectores alternativos basados en el HTML
                    selectores_descripcion = [
                        "p.sc-bnRxdl",      # Del information.html
                        "p.sc-gDeQiw",      # Alternativo
                        ".sc-bmlaxJ p",     # Párrafos en contenedor
                        ".content p",       # Fallback
                    ]

                    for selector in selectores_descripcion:
                        try:
                            desc_elems = driver.find_elements(By.CSS_SELECTOR, selector)
                            if desc_elems:
                                textos = []
                                for elem in desc_elems:
                                    texto = elem.text.strip()
                                    if len(texto) > 50:  # Solo párrafos largos
                                        textos.append(texto)

                                if textos:
                                    datos['descripcion'] = ' '.join(textos)
                                    print(f"   ✓ Descripción ({selector}): {len(datos['descripcion'])} caracteres")
                                    break
                        except:
                            continue
                    else:
                        # Último intento: buscar todos los párrafos largos
                        desc_elems = driver.find_elements(By.TAG_NAME, "p")
                        textos = []
                        for elem in desc_elems:
                            texto = elem.text.strip()
                            if len(texto) > 100:  # Solo párrafos largos
                                textos.append(texto)

                        if textos:
                            datos['descripcion'] = ' '.join(textos)
                            print(f"   ✓ Descripción (párrafos): {len(datos['descripcion'])} caracteres")
                        else:
                            datos['descripcion'] = None
                            print("   ✗ Descripción no encontrada")
                except:
                    datos['descripcion'] = None
                    print("   ✗ Descripción no encontrada")

            print(f"   ✅ Trabajo {index} procesado exitosamente")
            return datos

        except Exception as e:
            print(f"   ❌ Error al extraer trabajo {index}: {e}")
            return None

    def scrape_urls_lista(self, urls_lista):
        """Procesa una lista específica de URLs"""
        driver = None
        resultados = []

        try:
            driver = self.iniciar_driver()

            print(f"🚀 INICIANDO SCRAPING DE MULTITRABAJOS")
            print(f"📋 Total de URLs a procesar: {len(urls_lista)}")
            print("="*60)

            for index, url in enumerate(urls_lista, 1):
                try:
                    datos = self.extraer_detalles_trabajo(driver, url, index)

                    if datos:
                        resultados.append(datos)

                    # Pausa entre trabajos para evitar detección
                    if index < len(urls_lista):
                        pausa = random.uniform(2, 5)
                        print(f"   ⏸️  Pausando {pausa:.1f}s antes del siguiente trabajo...")
                        time.sleep(pausa)

                except Exception as e:
                    print(f"   ✗ Error procesando URL {index}: {e}")
                    continue

            print(f"\n🎯 SCRAPING COMPLETADO:")
            print(f"   • URLs procesadas: {len(urls_lista)}")
            print(f"   • Trabajos exitosos: {len(resultados)}")
            print(f"   • Tasa de éxito: {len(resultados)/len(urls_lista)*100:.1f}%")

            return resultados

        except Exception as e:
            print(f"❌ Error general: {e}")
            import traceback
            traceback.print_exc()
            return resultados

        finally:
            if driver:
                print("\n⏸️  Esperando 5s antes de cerrar...")
                time.sleep(5)
                driver.quit()

    def guardar_resultados(self, jobs, filename='multitrabajos_desarrolladores.csv'):
        """Guarda trabajos en CSV"""
        if jobs:
            df = pd.DataFrame(jobs)

            # Reordenar columnas
            columnas_orden = [
                'index', 'titulo', 'empresa', 'ubicacion', 'salario',
                'modalidad', 'jornada', 'categoria', 'seniority', 'vacantes',
                'descripcion', 'url'
            ]
            df = df[[col for col in columnas_orden if col in df.columns]]

            df.to_csv(filename, index=False, encoding='utf-8-sig')

            print(f"\n💾 Archivo guardado: {filename}")
            print(f"   Total trabajos: {len(jobs)}")

            # Resumen
            print("\n📊 RESUMEN:")
            print(f"   Con título: {df['titulo'].notna().sum()}")
            print(f"   Con empresa: {df['empresa'].notna().sum()}")
            print(f"   Con ubicación: {df['ubicacion'].notna().sum()}")
            print(f"   Con modalidad: {df['modalidad'].notna().sum()}")
            print(f"   Con jornada: {df['jornada'].notna().sum()}")
            print(f"   Con descripción: {df['descripcion'].notna().sum()}")

        else:
            print("\n❌ No se encontraron trabajos para guardar")


def main():
    print("="*60)
    print("🚀 SCRAPER DE MULTITRABAJOS - QA")  # CAMBIO 2: Título
    print("="*60)
    print("\n📋 INFORMACIÓN:")
    print("   • Procesará 6 URLs específicas")  # CAMBIO 3: Cantidad actualizada
    print("   • Extraerá: título, empresa, ubicación, modalidad, jornada, descripción")
    print("   • Solo para fines EDUCATIVOS")
    print("   • Tiempo estimado: ~3-5 minutos")  # CAMBIO 4: Tiempo ajustado
    print("   • Con pausas para evitar detección\n")

    input("Presiona ENTER para continuar...")

    # CAMBIO 5: Lista de URLs de QA
    urls_trabajos = [
        "https://www.multitrabajos.com/empleos/supervisor-qa-qc-electrico-pmec-ingenieria-y-construccion-metalmecanica-ecuatoriana-s.a-1117978050.html",
        "https://www.multitrabajos.com/empleos/supervisor-qa-qc-civil-1117986476.html",
        "https://www.multitrabajos.com/empleos/qa-1117975850.html",
        "https://www.multitrabajos.com/empleos/tecnico-qa-qc-civil-sedemi-1118005537.html",
        "https://www.multitrabajos.com/empleos/tecnico-qa-qc-civil-sedemi-1118005546.html",
        "https://www.multitrabajos.com/empleos/ingeniero-de-procesos-qa-1118022535.html"
    ]

    scraper = MultitrabajosScraper()

    # Procesar las URLs
    jobs = scraper.scrape_urls_lista(urls_trabajos)

    # CAMBIO 6: Guardar con nombre específico
    scraper.guardar_resultados(jobs, filename='multitrabajos_qa.csv')

    print("\n" + "="*60)
    print("✅ PROCESO FINALIZADO")
    print("="*60)


if __name__ == "__main__":
    main()