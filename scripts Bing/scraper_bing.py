from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
from datetime import datetime
import time
import random

class BingJobsDetailedScraper:
    def __init__(self):
        self.base_url = "https://www.bing.com/jobs"
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]

    def iniciar_driver(self):
        """Configura Chrome con anti-detección"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'user-agent={random.choice(self.user_agents)}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')

        driver = webdriver.Chrome(options=chrome_options)

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

    def scroll_para_cargar_mas(self, driver):
        """SCROLL ULTRA AGRESIVO para cargar los 95+ trabajos"""
        try:
            lista_trabajos = driver.find_element(By.CSS_SELECTOR, ".jb_l2_list")

            intentos_sin_cambio = 0
            max_intentos_sin_cambio = 10
            scroll_count = 0
            max_scrolls = 30  # CAMBIO: Reducido de 200 a 100

            print("   🔄 Iniciando carga COMPLETA de trabajos...")

            while scroll_count < max_scrolls and intentos_sin_cambio < max_intentos_sin_cambio:
                # Contar trabajos actuales
                trabajos_antes = len(driver.find_elements(By.CSS_SELECTOR, ".jb_jlc"))

                # ===== ESTRATEGIA 1: Scroll al FINAL del contenedor =====
                driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
                    lista_trabajos
                )
                time.sleep(2.0)

                # ===== ESTRATEGIA 2: Scroll con el mouse wheel (más realista) =====
                for _ in range(3):
                    driver.execute_script(
                        "arguments[0].scrollBy(0, 500);",
                        lista_trabajos
                    )
                    time.sleep(0.5)

                # ===== ESTRATEGIA 3: Scroll al último elemento visible =====
                try:
                    ultimo_trabajo = driver.find_elements(By.CSS_SELECTOR, ".jb_jlc")[-1]
                    driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});",
                        ultimo_trabajo
                    )
                    time.sleep(1.5)
                except:
                    pass

                # ===== ESTRATEGIA 4: Simular movimiento de mouse =====
                driver.execute_script("window.scrollBy(0, 100);")
                time.sleep(0.3)
                driver.execute_script("window.scrollBy(0, -50);")
                time.sleep(0.3)

                # ===== ESTRATEGIA 5: Buscar botón "Ver más" =====
                try:
                    botones_ver_mas = driver.find_elements(By.XPATH,
                        "//button[contains(text(), 'Show more') or contains(text(), 'Ver más') or contains(@class, 'show-more')]")
                    for btn in botones_ver_mas:
                        if btn.is_displayed():
                            driver.execute_script("arguments[0].click();", btn)
                            print("      ✓ Click en 'Ver más'")
                            time.sleep(2)
                except:
                    pass

                # Esperar a que cargue contenido nuevo
                time.sleep(2.5)

                # Verificar si aumentó el número de trabajos
                trabajos_despues = len(driver.find_elements(By.CSS_SELECTOR, ".jb_jlc"))

                if trabajos_despues > trabajos_antes:
                    print(f"      📊 Trabajos: {trabajos_despues} (+{trabajos_despues - trabajos_antes})")
                    intentos_sin_cambio = 0
                else:
                    intentos_sin_cambio += 1
                    print(f"      ⏳ Sin cambios... ({intentos_sin_cambio}/{max_intentos_sin_cambio})")

                scroll_count += 1

            total_final = len(driver.find_elements(By.CSS_SELECTOR, ".jb_jlc"))

            if intentos_sin_cambio >= max_intentos_sin_cambio:
                print(f"   ✅ Carga completa (sin más cambios): {total_final} trabajos")
            else:
                print(f"   ⚠️  Límite de scrolls alcanzado: {total_final} trabajos")

            return total_final

        except Exception as e:
            print(f"   ⚠️  Error en scroll: {e}")
            import traceback
            traceback.print_exc()
            return len(driver.find_elements(By.CSS_SELECTOR, ".jb_jlc"))

    def buscar_trabajos(self, driver, termino_busqueda, ubicacion="Ecuador"):
        """Realiza la búsqueda inicial"""
        url = f"https://www.bing.com/jobs?q={termino_busqueda.replace(' ', '+')}&l={ubicacion}"
        print(f"Accediendo a: {url}")
        driver.get(url)

        # Esperar a que cargue la página
        time.sleep(5)

    def obtener_trabajos_visibles(self, driver):
        """Obtiene los trabajos actualmente visibles en la lista"""
        trabajos_data = []

        try:
            # Esperar a que haya trabajos cargados
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jb_jlc")))

            # Obtener todos los elementos de trabajo visibles
            trabajos = driver.find_elements(By.CLASS_NAME, "jb_jlc")
            print(f"Trabajos encontrados en esta iteración: {len(trabajos)}")

            for idx, trabajo in enumerate(trabajos, 1):
                try:
                    # Intentar obtener el ID único del trabajo
                    job_id = trabajo.get_attribute('data-jobid') or trabajo.get_attribute('id') or f"job_{idx}_{int(time.time())}"

                    # Extraer información básica sin hacer clic
                    try:
                        titulo = trabajo.find_element(By.CLASS_NAME, "jbovrly_title").text
                    except:
                        titulo = "No disponible"

                    try:
                        empresa = trabajo.find_element(By.CLASS_NAME, "jbovrly_cmpny").text
                    except:
                        empresa = "No disponible"

                    try:
                        ubicacion = trabajo.find_element(By.CLASS_NAME, "jbovrly_lj").text
                    except:
                        ubicacion = "No disponible"

                    try:
                        fecha = trabajo.find_element(By.CLASS_NAME, "jb_postedDate").text
                    except:
                        fecha = "No disponible"

                    trabajos_data.append({
                        'job_id': job_id,
                        'titulo': titulo,
                        'empresa': empresa,
                        'ubicacion': ubicacion,
                        'fecha_publicacion': fecha,
                        'url': driver.current_url
                    })

                except Exception as e:
                    print(f"Error extrayendo trabajo {idx}: {e}")
                    continue

        except Exception as e:
            print(f"Error general en obtener_trabajos_visibles: {e}")

        return trabajos_data

    def scrape_trabajos_con_scroll(self, driver, max_scrolls=20):
        """
        Scrapea trabajos haciendo scroll gradual
        """
        todos_trabajos = []
        trabajos_unicos = set()
        scroll_sin_cambios = 0
        max_sin_cambios = 3

        try:
            # Encontrar el contenedor de la lista de trabajos
            contenedor = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jb_l2_cardlist"))
            )
            print("Contenedor de trabajos encontrado")

            for scroll_num in range(max_scrolls):
                print(f"\n--- Scroll {scroll_num + 1}/{max_scrolls} ---")

                # Obtener trabajos visibles en esta posición
                trabajos_actuales = self.obtener_trabajos_visibles(driver)

                # Contar cuántos trabajos nuevos se encontraron
                trabajos_nuevos = 0
                for trabajo in trabajos_actuales:
                    job_id = trabajo['job_id']
                    if job_id not in trabajos_unicos:
                        trabajos_unicos.add(job_id)
                        todos_trabajos.append(trabajo)
                        trabajos_nuevos += 1

                print(f"Trabajos nuevos encontrados: {trabajos_nuevos}")
                print(f"Total acumulado: {len(todos_trabajos)}")

                # Si no se encontraron trabajos nuevos, incrementar contador
                if trabajos_nuevos == 0:
                    scroll_sin_cambios += 1
                    print(f"Sin trabajos nuevos ({scroll_sin_cambios}/{max_sin_cambios})")

                    if scroll_sin_cambios >= max_sin_cambios:
                        print("No hay más trabajos nuevos. Finalizando...")
                        break
                else:
                    scroll_sin_cambios = 0

                # Hacer scroll
                if scroll_num < max_scrolls - 1:
                    scroll_exitoso = self.scroll_gradual(driver, contenedor)
                    if not scroll_exitoso:
                        print("No se pudo hacer más scroll")
                        break

                    # Esperar a que carguen nuevos trabajos
                    time.sleep(2)

        except Exception as e:
            print(f"Error en scrape_trabajos_con_scroll: {e}")

        return todos_trabajos

    def extraer_detalles_trabajo(self, driver, index):
        """Extrae detalles del trabajo desde el panel derecho"""
        try:
            # Esperar más tiempo a que cargue el panel
            time.sleep(3)

            datos = {}

            # DEBUG: Guardar HTML si es uno de los primeros 3
            if index <= 3:
                try:
                    with open(f'debug_trabajo_{index}.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"      💾 HTML guardado: debug_trabajo_{index}.html")
                except:
                    pass

            # 1. TÍTULO (múltiples intentos)
            try:
                titulo_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jb_title"))
                )
                datos['titulo'] = self.limpiar_texto(titulo_elem.text)
            except:
                try:
                    titulo_elem = driver.find_element(By.XPATH, "//div[contains(@class, 'title')]")
                    datos['titulo'] = self.limpiar_texto(titulo_elem.text)
                except:
                    datos['titulo'] = None

            if datos['titulo']:
                print(f"      ✓ Título: {datos['titulo']}")
            else:
                print("      ✗ Título no encontrado")

            # 2. EMPRESA
            try:
                empresa_elem = driver.find_element(By.CSS_SELECTOR, ".jbpnl_coLoc__co")
                datos['empresa'] = self.limpiar_texto(empresa_elem.text)
            except:
                try:
                    empresa_elem = driver.find_element(By.XPATH, "//div[contains(@class, 'coLoc')]//div[1]")
                    datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                except:
                    datos['empresa'] = None

            if datos['empresa']:
                print(f"      ✓ Empresa: {datos['empresa']}")

            # 3. UBICACIÓN
            try:
                ubicacion_elem = driver.find_element(By.CSS_SELECTOR, ".jbpnl_coLoc__loc")
                datos['ubicacion'] = self.limpiar_texto(ubicacion_elem.text)
            except:
                try:
                    ubicacion_elem = driver.find_element(By.XPATH, "//div[contains(@class, 'coLoc')]//div[contains(text(), ',')]")
                    datos['ubicacion'] = self.limpiar_texto(ubicacion_elem.text)
                except:
                    datos['ubicacion'] = None

            if datos['ubicacion']:
                print(f"      ✓ Ubicación: {datos['ubicacion']}")

            # 4. MODALIDAD
            try:
                page_text = driver.find_element(By.CSS_SELECTOR, ".jb_l2_jbpnl").text

                if 'Remote' in page_text or 'remote' in page_text:
                    datos['modalidad'] = 'Remoto'
                elif 'On-site' in page_text or 'Presencial' in page_text:
                    datos['modalidad'] = 'Presencial'
                elif 'Hybrid' in page_text or 'Híbrido' in page_text:
                    datos['modalidad'] = 'Híbrido'
                else:
                    datos['modalidad'] = None
            except:
                datos['modalidad'] = None

            if datos['modalidad']:
                print(f"      ✓ Modalidad: {datos['modalidad']}")

            # 5. DESCRIPCIÓN
            try:
                descripcion_elem = driver.find_element(By.CSS_SELECTOR, ".jbpnl_desc")
                datos['descripcion'] = self.limpiar_texto(descripcion_elem.text)
            except:
                try:
                    panel = driver.find_element(By.CSS_SELECTOR, ".jb_l2_jbpnl")
                    datos['descripcion'] = self.limpiar_texto(panel.text)
                except:
                    datos['descripcion'] = None

            if datos['descripcion']:
                print(f"      ✓ Descripción: {len(datos['descripcion'])} caracteres")

            return datos

        except Exception as e:
            print(f"      ❌ Error al extraer: {e}")
            return None

    def guardar_resultados(self, jobs, filename='bing_jobs_desarrolladores.csv'):
        """Guarda trabajos en CSV"""
        if jobs:
            df = pd.DataFrame(jobs)

            # Reordenar columnas
            columnas_orden = ['index', 'titulo', 'empresa', 'ubicacion', 'modalidad', 'descripcion']
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
            print(f"   Con descripción: {df['descripcion'].notna().sum()}")
        else:
            print("\n❌ No se encontraron trabajos para guardar")


def main():
    # CAMBIO 1: Cambiar término de búsqueda
    termino_busqueda = "analista de datos"
    ubicacion = "Ecuador"

    print(f"🔍 Iniciando búsqueda de: '{termino_busqueda}' en {ubicacion}")
    print("="*60)
    print("📌 PROCESANDO SOLO TRABAJOS 501-600 (LOTE 6 FALTANTE)")
    print("="*60)

    scraper = BingJobsDetailedScraper()
    driver = scraper.iniciar_driver()

    try:
        # CAMBIO 2: Usar la nueva URL de analista de datos
        url = "https://www.bing.com/jobs?q=analista+de+datos&go=Buscar&qs=ds&form=JOBL2P&scp=0&c=1"
        print(f"📄 Accediendo a: {url}")
        driver.get(url)

        # Esperar carga inicial
        time.sleep(random.uniform(5, 8))

        # Verificar Cloudflare
        if 'cloudflare' in driver.page_source.lower():
            print("   ⚠️  Cloudflare detectado - Esperando...")
            time.sleep(10)

        # SCROLL ULTRA AGRESIVO para cargar TODOS
        total_cargados = scraper.scroll_para_cargar_mas(driver)

        # ===== VOLVER AL INICIO DE LA LISTA =====
        print("\n   ⬆️  Regresando al inicio de la lista...")
        try:
            lista_trabajos = driver.find_element(By.CSS_SELECTOR, ".jb_l2_list")
            driver.execute_script("arguments[0].scrollTo(0, 0);", lista_trabajos)
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            print("   ✅ Posición inicial restaurada")
        except Exception as e:
            print(f"   ⚠️  No se pudo volver al inicio: {e}")

        # Obtener lista FINAL de trabajos
        job_cards = driver.find_elements(By.CSS_SELECTOR, ".jb_jlc")
        print(f"\n   🎯 TOTAL ENCONTRADO: {len(job_cards)} trabajos")

        # ===== NUEVO: SOLO PROCESAR DEL 501 AL 600 =====
        INICIO = 500  # Índice 500 = trabajo 501
        FIN = 600     # Índice 600 = trabajo 600

        if len(job_cards) < FIN:
            print(f"   ⚠️  Solo hay {len(job_cards)} trabajos, ajustando rango...")
            FIN = len(job_cards)

        if len(job_cards) <= INICIO:
            print(f"   ❌ No hay suficientes trabajos para procesar desde el {INICIO+1}")
            return

        # Obtener solo los trabajos del rango 501-600
        trabajos_a_procesar = job_cards[INICIO:FIN]
        print(f"   📌 PROCESANDO: Trabajos {INICIO+1} a {FIN} ({len(trabajos_a_procesar)} trabajos)")

        resultados = []

        # Procesar solo el rango específico (SIN LOTES)
        for idx, card in enumerate(trabajos_a_procesar):
            i = INICIO + idx + 1  # Número real del trabajo (501, 502, 503...)

            try:
                print(f"\n   [{i}/{FIN}] Procesando trabajo {i}...")

                # Scroll al elemento
                lista_trabajos = driver.find_element(By.CSS_SELECTOR, ".jb_l2_list")
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[1];",
                    lista_trabajos,
                    card.location['y'] - 200
                )
                time.sleep(0.8)

                # Click
                try:
                    card.click()
                except:
                    driver.execute_script("arguments[0].click();", card)

                # Esperar panel
                time.sleep(2)

                # Extraer detalles
                datos = scraper.extraer_detalles_trabajo(driver, i)

                if datos:
                    datos['index'] = i
                    resultados.append(datos)
                    print(f"      ✅ Trabajo {i} procesado exitosamente")
                else:
                    print(f"      ⚠️  No se extrajeron datos del trabajo {i}")

                time.sleep(random.uniform(1.5, 2.5))

            except Exception as e:
                print(f"   ✗ Error en trabajo {i}: {e}")
                try:
                    driver.save_screenshot(f'error_trabajo_{i}.png')
                except:
                    pass
                continue

        # Guardar con nombre específico para el lote 6 faltante
        scraper.guardar_resultados(resultados, filename='bing_jobs_analista_datos_lote6_501_600.csv')

        print(f"\n🎉 LOTE 6 FALTANTE COMPLETADO:")
        print(f"   • Trabajos procesados: {len(resultados)}")
        print(f"   • Rango: {INICIO+1} a {FIN}")
        print(f"   • Archivo: bing_jobs_analista_datos_lote6_501_600.csv")

    except Exception as e:
        print(f"❌ Error en main: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n⏳ Cerrando navegador en 5 segundos...")
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    main()
