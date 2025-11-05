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

class IndeedAnalistaDataScraper:  # CAMBIO 1: Nuevo nombre de clase
    def __init__(self):
        self.base_url = "https://ec.indeed.com"
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
        """Limpia texto eliminando espacios extra"""
        if not texto:
            return None
        return ' '.join(texto.split()).strip()

    def obtener_trabajos_pagina_actual(self, driver):
        """Obtiene todos los trabajos de la página actual"""
        try:
            # Esperar a que carguen los trabajos
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='job_']"))
            )

            # Obtener todos los elementos de trabajo
            trabajos = driver.find_elements(By.CSS_SELECTOR, "[class*='job_'][class*='result']")

            print(f"   📋 Trabajos encontrados en esta página: {len(trabajos)}")

            return trabajos

        except TimeoutException:
            print("   ⚠️  No se encontraron trabajos en esta página")
            return []

    def extraer_detalles_trabajo(self, driver, trabajo_elem, index):
        """Hace clic en un trabajo y extrae sus detalles"""
        try:
            # Hacer clic en el trabajo
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trabajo_elem)
            time.sleep(1)
            trabajo_elem.click()

            print(f"      👆 Click en trabajo {index}")

            # Esperar a que cargue el panel de detalles
            time.sleep(3)

            datos = {}

            # 1. TÍTULO del trabajo
            try:
                titulo_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='jobsearch-JobInfoHeader-title']"))
                )
                datos['titulo'] = self.limpiar_texto(titulo_elem.text)
                print(f"      ✓ Título: {datos['titulo']}")
            except:
                try:
                    # Intento alternativo
                    titulo_elem = driver.find_element(By.CSS_SELECTOR, ".jobsearch-JobInfoHeader-title")
                    datos['titulo'] = self.limpiar_texto(titulo_elem.text)
                    print(f"      ✓ Título: {datos['titulo']}")
                except:
                    datos['titulo'] = None
                    print("      ✗ Título no encontrado")

            # 2. EMPRESA
            try:
                empresa_elem = driver.find_element(By.CSS_SELECTOR, "[data-testid='inlineHeader-companyName']")
                datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                print(f"      ✓ Empresa: {datos['empresa']}")
            except:
                try:
                    empresa_elem = driver.find_element(By.CSS_SELECTOR, "[data-company-name='true']")
                    datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                    print(f"      ✓ Empresa: {datos['empresa']}")
                except:
                    datos['empresa'] = None
                    print("      ✗ Empresa no encontrada")

            # 3. UBICACIÓN
            try:
                ubicacion_elem = driver.find_element(By.CSS_SELECTOR, "[data-testid='inlineHeader-companyLocation']")
                datos['ubicacion'] = self.limpiar_texto(ubicacion_elem.text)
                print(f"      ✓ Ubicación: {datos['ubicacion']}")
            except:
                try:
                    ubicacion_elem = driver.find_element(By.CSS_SELECTOR, "[data-testid='jobsearch-JobInfoHeader-companyLocation']")
                    datos['ubicacion'] = self.limpiar_texto(ubicacion_elem.text)
                    print(f"      ✓ Ubicación: {datos['ubicacion']}")
                except:
                    datos['ubicacion'] = None
                    print("      ✗ Ubicación no encontrada")

            # 4. SALARIO (si está disponible)
            try:
                salario_elem = driver.find_element(By.CSS_SELECTOR, "[data-testid='jobsearch-CollapsedEmbeddedHeader-salary']")
                datos['salario'] = self.limpiar_texto(salario_elem.text)
                if datos['salario']:
                    print(f"      ✓ Salario: {datos['salario']}")
                else:
                    datos['salario'] = None
            except:
                datos['salario'] = None

            # 5. DESCRIPCIÓN COMPLETA
            try:
                descripcion_elem = driver.find_element(By.CSS_SELECTOR, "#jobDescriptionText")
                datos['descripcion'] = self.limpiar_texto(descripcion_elem.text)
                print(f"      ✓ Descripción: {len(datos['descripcion'])} caracteres")
            except:
                try:
                    descripcion_elem = driver.find_element(By.CSS_SELECTOR, ".jobsearch-JobComponent-description")
                    datos['descripcion'] = self.limpiar_texto(descripcion_elem.text)
                    print(f"      ✓ Descripción: {len(datos['descripcion'])} caracteres")
                except:
                    datos['descripcion'] = None
                    print("      ✗ Descripción no encontrada")

            # 6. MODALIDAD (extraer del texto de la descripción)
            try:
                if datos['descripcion']:
                    desc_text = datos['descripcion'].lower()
                    if any(word in desc_text for word in ['remoto', 'remote', 'teletrabajo', 'desde casa']):
                        datos['modalidad'] = 'Remoto'
                    elif any(word in desc_text for word in ['presencial', 'oficina', 'on-site']):
                        datos['modalidad'] = 'Presencial'
                    elif any(word in desc_text for word in ['híbrido', 'hybrid', 'mixto']):
                        datos['modalidad'] = 'Híbrido'
                    else:
                        datos['modalidad'] = None
                else:
                    datos['modalidad'] = None

                if datos['modalidad']:
                    print(f"      ✓ Modalidad: {datos['modalidad']}")
            except:
                datos['modalidad'] = None

            # 7. TIPO DE CONTRATO (si está disponible)
            try:
                # Buscar en metadatos del trabajo
                meta_elems = driver.find_elements(By.CSS_SELECTOR, ".jobMetaDataGroup li")
                datos['tipo_contrato'] = None
                for elem in meta_elems:
                    text = elem.text.lower()
                    if any(word in text for word in ['tiempo completo', 'full-time', 'medio tiempo', 'part-time', 'contrato', 'temporal']):
                        datos['tipo_contrato'] = self.limpiar_texto(elem.text)
                        break

                if datos['tipo_contrato']:
                    print(f"      ✓ Tipo contrato: {datos['tipo_contrato']}")
            except:
                datos['tipo_contrato'] = None

            return datos

        except Exception as e:
            print(f"      ❌ Error al extraer detalles: {e}")
            return None

    def ir_siguiente_pagina(self, driver):
        """Intenta ir a la siguiente página"""
        try:
            # Buscar el botón "Siguiente" o ">"
            botones_siguiente = [
                "[data-testid='pagination-page-next']",
                "a[aria-label*='siguiente']",
                "a[aria-label*='Página siguiente']"
            ]

            for selector in botones_siguiente:
                try:
                    boton_siguiente = driver.find_element(By.CSS_SELECTOR, selector)
                    if boton_siguiente.is_enabled():
                        print("   ▶️  Yendo a la siguiente página...")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_siguiente)
                        time.sleep(1)
                        boton_siguiente.click()
                        time.sleep(random.uniform(3, 5))
                        return True
                except:
                    continue

            print("   ⏹️  No se encontró botón 'Siguiente'")
            return False

        except Exception as e:
            print(f"   ⚠️  Error al ir a siguiente página: {e}")
            return False

    def obtener_numero_pagina_actual(self, driver):
        """Obtiene el número de página actual"""
        try:
            pagina_actual = driver.find_element(By.CSS_SELECTOR, "[data-testid='pagination-page-current']")
            return int(pagina_actual.text)
        except:
            return 1

    def scrape_indeed_jobs(self, url, max_paginas=5):
        """Scrapea trabajos de Indeed con paginación"""
        driver = None
        resultados = []

        try:
            print(f"\n📄 Accediendo a: {url}")
            driver = self.iniciar_driver()
            driver.get(url)

            # Esperar carga inicial
            time.sleep(random.uniform(5, 8))

            pagina_actual = 1
            total_trabajos_procesados = 0

            while pagina_actual <= max_paginas:
                print(f"\n{'='*60}")
                print(f"📄 PÁGINA {pagina_actual}")
                print(f"{'='*60}")

                # Obtener trabajos de la página actual
                trabajos = self.obtener_trabajos_pagina_actual(driver)

                if not trabajos:
                    print("   ❌ No hay trabajos en esta página")
                    break

                # Procesar cada trabajo
                for i, trabajo in enumerate(trabajos, 1):
                    index_global = total_trabajos_procesados + i

                    try:
                        print(f"\n   [{index_global}] Procesando trabajo {i}/{len(trabajos)}...")

                        # Extraer detalles
                        datos = self.extraer_detalles_trabajo(driver, trabajo, index_global)

                        if datos:
                            datos['index'] = index_global
                            datos['pagina'] = pagina_actual
                            resultados.append(datos)
                            print(f"      ✅ Trabajo {index_global} procesado exitosamente")
                        else:
                            print(f"      ⚠️  No se extrajeron datos del trabajo {index_global}")

                        # Pausa entre trabajos
                        time.sleep(random.uniform(2, 4))

                    except Exception as e:
                        print(f"   ✗ Error en trabajo {index_global}: {e}")
                        continue

                total_trabajos_procesados += len(trabajos)

                # Intentar ir a la siguiente página
                if pagina_actual < max_paginas:
                    if self.ir_siguiente_pagina(driver):
                        pagina_actual += 1
                        # Verificar que realmente cambió de página
                        nueva_pagina = self.obtener_numero_pagina_actual(driver)
                        if nueva_pagina <= pagina_actual - 1:
                            print("   ⚠️  No se pudo avanzar a la siguiente página")
                            break
                    else:
                        print("   🏁 No hay más páginas disponibles")
                        break
                else:
                    print(f"   🏁 Límite de páginas alcanzado ({max_paginas})")
                    break

            print(f"\n🎯 RESUMEN FINAL:")
            print(f"   • Páginas procesadas: {pagina_actual}")
            print(f"   • Total trabajos encontrados: {total_trabajos_procesados}")
            print(f"   • Trabajos procesados exitosamente: {len(resultados)}")

            return resultados

        except Exception as e:
            print(f"   ❌ Error general: {e}")
            import traceback
            traceback.print_exc()
            return resultados

        finally:
            if driver:
                print("\n   ⏸️  Esperando 5s antes de cerrar...")
                time.sleep(5)
                driver.quit()

    def extraer_detalles_trabajo_individual(self, driver, url, index):
        """Extrae detalles de un trabajo específico visitando su URL directamente"""
        try:
            print(f"\n{'='*60}")
            print(f"📋 TRABAJO {index}/23")  # CAMBIO 2: Total de URLs únicas
            print(f"{'='*60}")
            print(f"📄 URL: {url}")

            # Ir directamente a la URL del trabajo
            driver.get(url)
            time.sleep(random.uniform(4, 7))

            # Verificar que la página cargó
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='jobsearch-JobInfoHeader-title'], .jobsearch-JobInfoHeader-title"))
                )
                print("   ✅ Página cargada correctamente")
            except TimeoutException:
                print("   ❌ Error: Timeout al cargar la página")
                return None

            datos = {'url': url, 'index': index}

            # 1. TÍTULO del trabajo - SELECTORES BASADOS EN EL HTML
            try:
                titulo_elem = driver.find_element(By.CSS_SELECTOR, "[data-testid='jobsearch-JobInfoHeader-title']")
                datos['titulo'] = self.limpiar_texto(titulo_elem.text)
                print(f"   ✓ Título: {datos['titulo']}")
            except:
                try:
                    titulo_elem = driver.find_element(By.CSS_SELECTOR, ".jobsearch-JobInfoHeader-title")
                    datos['titulo'] = self.limpiar_texto(titulo_elem.text)
                    print(f"   ✓ Título: {datos['titulo']}")
                except:
                    try:
                        titulo_elem = driver.find_element(By.CSS_SELECTOR, "h2.css-xtzn02")
                        datos['titulo'] = self.limpiar_texto(titulo_elem.text)
                        print(f"   ✓ Título: {datos['titulo']}")
                    except:
                        datos['titulo'] = None
                        print("   ✗ Título no encontrado")

            # 2. EMPRESA - SELECTORES CORREGIDOS
            try:
                empresa_elem = driver.find_element(By.CSS_SELECTOR, "[data-testid='inlineHeader-companyName']")
                datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                print(f"   ✓ Empresa: {datos['empresa']}")
            except:
                try:
                    empresa_elem = driver.find_element(By.CSS_SELECTOR, "[data-company-name='true']")
                    datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                    print(f"   ✓ Empresa: {datos['empresa']}")
                except:
                    try:
                        # Buscar en el enlace de la empresa
                        empresa_elem = driver.find_element(By.CSS_SELECTOR, ".css-1s1odts")
                        datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                        print(f"   ✓ Empresa: {datos['empresa']}")
                    except:
                        datos['empresa'] = None
                        print("   ✗ Empresa no encontrada")

            # 3. UBICACIÓN - SELECTORES CORREGIDOS
            try:
                ubicacion_elem = driver.find_element(By.CSS_SELECTOR, "[data-testid='inlineHeader-companyLocation']")
                datos['ubicacion'] = self.limpiar_texto(ubicacion_elem.text)
                print(f"   ✓ Ubicación: {datos['ubicacion']}")
            except:
                try:
                    ubicacion_elem = driver.find_element(By.CSS_SELECTOR, "[data-testid='jobsearch-JobInfoHeader-companyLocation']")
                    datos['ubicacion'] = self.limpiar_texto(ubicacion_elem.text)
                    print(f"   ✓ Ubicación: {datos['ubicacion']}")
                except:
                    try:
                        ubicacion_elem = driver.find_element(By.CSS_SELECTOR, ".css-1vysp2z")
                        datos['ubicacion'] = self.limpiar_texto(ubicacion_elem.text)
                        print(f"   ✓ Ubicación: {datos['ubicacion']}")
                    except:
                        datos['ubicacion'] = None
                        print("   ✗ Ubicación no encontrada")

            # 4. SALARIO (si está disponible)
            try:
                salario_elem = driver.find_element(By.CSS_SELECTOR, "[data-testid='jobsearch-CollapsedEmbeddedHeader-salary']")
                if salario_elem.text.strip():
                    datos['salario'] = self.limpiar_texto(salario_elem.text)
                    print(f"   ✓ Salario: {datos['salario']}")
                else:
                    datos['salario'] = None
            except:
                datos['salario'] = None

            # 5. DESCRIPCIÓN COMPLETA - SELECTOR CORREGIDO
            try:
                descripcion_elem = driver.find_element(By.CSS_SELECTOR, "#jobDescriptionText")
                datos['descripcion'] = self.limpiar_texto(descripcion_elem.text)
                print(f"   ✓ Descripción: {len(datos['descripcion'])} caracteres")
            except:
                try:
                    descripcion_elem = driver.find_element(By.CSS_SELECTOR, ".jobsearch-JobComponent-description")
                    datos['descripcion'] = self.limpiar_texto(descripcion_elem.text)
                    print(f"   ✓ Descripción: {len(datos['descripcion'])} caracteres")
                except:
                    try:
                        # Buscar la descripción en el contenedor específico
                        descripcion_elem = driver.find_element(By.CSS_SELECTOR, ".css-ci04xl")
                        datos['descripcion'] = self.limpiar_texto(descripcion_elem.text)
                        print(f"   ✓ Descripción: {len(datos['descripcion'])} caracteres")
                    except:
                        datos['descripcion'] = None
                        print("   ✗ Descripción no encontrada")

            # 6. MODALIDAD (extraer del texto de la descripción)
            try:
                if datos['descripcion']:
                    desc_text = datos['descripcion'].lower()
                    if any(word in desc_text for word in ['remoto', 'remote', 'teletrabajo', 'desde casa', 'work from home']):
                        datos['modalidad'] = 'Remoto'
                    elif any(word in desc_text for word in ['presencial', 'oficina', 'on-site', 'in-person']):
                        datos['modalidad'] = 'Presencial'
                    elif any(word in desc_text for word in ['híbrido', 'hybrid', 'mixto']):
                        datos['modalidad'] = 'Híbrido'
                    else:
                        datos['modalidad'] = None
                else:
                    datos['modalidad'] = None

                if datos['modalidad']:
                    print(f"   ✓ Modalidad: {datos['modalidad']}")
            except:
                datos['modalidad'] = None

            # 7. TIPO DE CONTRATO (buscar en la descripción)
            try:
                if datos['descripcion']:
                    desc_text = datos['descripcion'].lower()
                    if any(word in desc_text for word in ['tiempo completo', 'full-time', 'jornada completa']):
                        datos['tipo_contrato'] = 'Tiempo completo'
                    elif any(word in desc_text for word in ['medio tiempo', 'part-time', 'tiempo parcial']):
                        datos['tipo_contrato'] = 'Tiempo parcial'
                    elif any(word in desc_text for word in ['contrato', 'temporal', 'proyecto']):
                        datos['tipo_contrato'] = 'Contrato'
                    else:
                        datos['tipo_contrato'] = None
                else:
                    datos['tipo_contrato'] = None

                if datos['tipo_contrato']:
                    print(f"   ✓ Tipo contrato: {datos['tipo_contrato']}")
            except:
                datos['tipo_contrato'] = None

            print(f"   ✅ Trabajo {index} procesado exitosamente")
            return datos

        except Exception as e:
            print(f"   ❌ Error al extraer trabajo {index}: {e}")
            return None

    def scrape_analista_datos_lista(self, urls_lista):
        """Scrapea trabajos de QA desde una lista específica de URLs"""
        driver = None
        resultados = []

        try:
            print(f"\n🚀 INICIANDO SCRAPING DE INDEED QA")
            print(f"📋 Total de URLs a procesar: {len(urls_lista)}")
            print("="*60)

            driver = self.iniciar_driver()

            for index, url in enumerate(urls_lista, 1):
                try:
                    datos = self.extraer_detalles_trabajo_individual(driver, url, index)

                    if datos:
                        resultados.append(datos)

                    # Pausa entre trabajos para evitar detección
                    if index < len(urls_lista):
                        pausa = random.uniform(3, 6)
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

    def guardar_resultados(self, jobs, filename='indeed_jobs_analista_datos.csv'):  # CAMBIO 5: Nombre de archivo
        """Guarda trabajos en CSV"""
        if jobs:
            df = pd.DataFrame(jobs)

            # Reordenar columnas
            columnas_orden = ['index', 'titulo', 'empresa', 'ubicacion', 'salario', 'tipo_contrato', 'modalidad', 'descripcion', 'url']
            df = df[[col for col in columnas_orden if col in df.columns]]

            df.to_csv(filename, index=False, encoding='utf-8-sig')

            print(f"\n💾 Archivo guardado: {filename}")
            print(f"   Total trabajos: {len(jobs)}")

            # Resumen
            print("\n📊 RESUMEN:")
            print(f"   Con título: {df['titulo'].notna().sum()}")
            print(f"   Con empresa: {df['empresa'].notna().sum()}")
            print(f"   Con ubicación: {df['ubicacion'].notna().sum()}")
            print(f"   Con salario: {df['salario'].notna().sum()}")
            print(f"   Con modalidad: {df['modalidad'].notna().sum()}")
            print(f"   Con descripción: {df['descripcion'].notna().sum()}")

        else:
            print("\n❌ No se encontraron trabajos para guardar")


def main():
    print("="*60)
    print("🚀 SCRAPER DE INDEED JOBS - ANALISTA DE DATOS ECUADOR")  # CAMBIO 6: Título
    print("="*60)
    print("\n⚠️  ADVERTENCIAS:")
    print("   • Indeed tiene protecciones anti-bot")
    print("   • Este script es EXPERIMENTAL")
    print("   • Solo para fines EDUCATIVOS")
    print("   • Procesará 23 URLs específicas")  # CAMBIO 7: Cantidad
    print("   • Tiempo estimado: ~8-12 minutos\n")  # CAMBIO 8: Tiempo

    input("Presiona ENTER para continuar...")

    # CAMBIO 9: Lista de URLs de Analista de Datos
    urls_analista_datos = [
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=136181141c4abc02",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=29437157380918fb",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=fb53fd7188d8086b",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=c97090a390057abf",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=bb870c213f026bb7",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=a40de44cfda604d2",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=937dd67cc5729cd8",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=30a55442439bf582",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=a2a36b6dd2f43d29",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=b7b824585c4e0dc3",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=97982173ad13285a",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=a15748a9f9ac6b5b",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=a0272642a524d1a9",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=0e8b3b7680ca51f2",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&start=10&vjk=8e06a3d7aff77011",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&start=10&vjk=4f244cffe822d30c",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&start=10&vjk=32610f2f8051527b",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&start=10&vjk=5bae04cad96b150d",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&start=10&vjk=f9f18c0feff1084a",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&start=10&vjk=d5e70920cdbab8fb",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&start=10&vjk=25b8bc0fd44eeeda",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&start=10&vjk=c19ee0a0ce72b4ed",
        "https://ec.indeed.com/jobs?q=analista+de+datos&l=Ecuador&radius=25&from=searchOnDesktopSerp%2Cwhereautocomplete&start=10&vjk=247e11bc996c69a1"
    ]

    # Eliminar duplicados manteniendo orden
    urls_analista_unicas = []
    seen = set()
    for url in urls_analista_datos:
        if url not in seen:
            urls_analista_unicas.append(url)
            seen.add(url)

    print(f"URLs únicas a procesar: {len(urls_analista_unicas)}")

    scraper = IndeedAnalistaDataScraper()  # CAMBIO 10: Nueva clase

    # Procesar las URLs
    jobs = scraper.scrape_analista_datos_lista(urls_analista_unicas)  # CAMBIO 11: Nuevo método

    # Guardar resultados
    scraper.guardar_resultados(jobs)

    print("\n" + "="*60)
    print("✅ PROCESO FINALIZADO")
    print("="*60)


if __name__ == "__main__":
    main()