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

class AccionTrabajoScraper:
    def __init__(self):
        self.base_url = "https://ec.acciontrabajo.com"
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

    def scroll_para_cargar_trabajos(self, driver, max_scrolls=15):
        """Hace scroll en el lado derecho para cargar todos los trabajos"""
        try:
            # Buscar el contenedor de trabajos (lado derecho)
            contenedor_trabajos = driver.find_element(By.CSS_SELECTOR, ".results_page")
            print(f"   🔄 Haciendo scroll para cargar trabajos (máximo {max_scrolls} scrolls)...")

            trabajos_anteriores = 0
            scrolls_sin_cambios = 0
            max_sin_cambios = 5

            for scroll in range(max_scrolls):
                # Contar trabajos actuales
                trabajos_actuales = len(driver.find_elements(By.CSS_SELECTOR, ".listing_url"))

                # Hacer scroll hacia abajo en el contenedor
                driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
                    contenedor_trabajos
                )

                # También scroll en la ventana principal
                driver.execute_script("window.scrollBy(0, 500);")

                # Pausa para que cargue
                time.sleep(2)

                # Verificar si se cargaron más trabajos
                nuevos_trabajos = len(driver.find_elements(By.CSS_SELECTOR, ".listing_url"))

                if nuevos_trabajos > trabajos_actuales:
                    print(f"      📊 Scroll {scroll + 1}: {nuevos_trabajos} trabajos (+{nuevos_trabajos - trabajos_actuales})")
                    scrolls_sin_cambios = 0
                    trabajos_anteriores = nuevos_trabajos
                else:
                    scrolls_sin_cambios += 1
                    print(f"      ⏳ Scroll {scroll + 1}: Sin cambios ({scrolls_sin_cambios}/{max_sin_cambios})")

                    if scrolls_sin_cambios >= max_sin_cambios:
                        print("      ✅ No se cargan más trabajos")
                        break

            total_final = len(driver.find_elements(By.CSS_SELECTOR, ".listing_url"))
            print(f"   🎯 Total trabajos cargados: {total_final}")
            return total_final

        except Exception as e:
            print(f"   ⚠️  Error en scroll: {e}")
            return len(driver.find_elements(By.CSS_SELECTOR, ".listing_url"))

    def extraer_detalles_trabajo(self, driver, index):
        """Extrae detalles del trabajo desde el panel izquierdo"""
        try:
            # Esperar a que cargue el panel de detalles
            time.sleep(3)

            datos = {}

            # 1. TÍTULO del trabajo
            try:
                titulo_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.observe_vacancy"))
                )
                datos['titulo'] = self.limpiar_texto(titulo_elem.text)
                print(f"      ✓ Título: {datos['titulo']}")
            except:
                try:
                    titulo_elem = driver.find_element(By.CSS_SELECTOR, ".observe_vacancy")
                    datos['titulo'] = self.limpiar_texto(titulo_elem.text)
                    print(f"      ✓ Título: {datos['titulo']}")
                except:
                    datos['titulo'] = None
                    print("      ✗ Título no encontrado")

            # 2. EMPRESA
            try:
                empresa_elem = driver.find_element(By.CSS_SELECTOR, ".tdu.fwb")
                datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                print(f"      ✓ Empresa: {datos['empresa']}")
            except:
                try:
                    # Buscar empresa en enlace
                    empresa_elem = driver.find_element(By.CSS_SELECTOR, "a[href*='/empresas/'] span.tdu.fwb")
                    datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                    print(f"      ✓ Empresa: {datos['empresa']}")
                except:
                    datos['empresa'] = None
                    print("      ✗ Empresa no encontrada")

            # 3. UBICACIÓN
            try:
                ubicacion_elem = driver.find_element(By.CSS_SELECTOR, ".wsn.fwb")
                datos['ubicacion'] = self.limpiar_texto(ubicacion_elem.text)
                print(f"      ✓ Ubicación: {datos['ubicacion']}")
            except:
                datos['ubicacion'] = None

            # 4. CARACTERÍSTICAS/FEATURES del trabajo
            try:
                features_container = driver.find_element(By.CSS_SELECTOR, ".vacancy_features")
                features = features_container.find_elements(By.CSS_SELECTOR, ".vacancy_feature")

                caracteristicas = []
                datos['salario'] = None
                datos['experiencia'] = None
                datos['jornada'] = None
                datos['modalidad'] = None

                for feature in features:
                    texto = self.limpiar_texto(feature.text)
                    if texto:
                        caracteristicas.append(texto)

                        # Extraer información específica
                        texto_lower = texto.lower()

                        # Salario
                        if 'usd' in texto_lower or '$' in texto:
                            datos['salario'] = texto

                        # Experiencia
                        if any(word in texto_lower for word in ['años', 'experiencia', 'año']):
                            datos['experiencia'] = texto

                        # Jornada
                        if any(word in texto_lower for word in ['completa', 'parcial', 'temporal', 'medio tiempo', 'jornada']):
                            datos['jornada'] = texto

                        # Modalidad
                        if any(word in texto_lower for word in ['remoto', 'presencial', 'híbrido', 'teletrabajo']):
                            datos['modalidad'] = texto

                datos['caracteristicas'] = ' | '.join(caracteristicas)

                if datos['salario']:
                    print(f"      ✓ Salario: {datos['salario']}")
                if datos['experiencia']:
                    print(f"      ✓ Experiencia: {datos['experiencia']}")
                if datos['modalidad']:
                    print(f"      ✓ Modalidad: {datos['modalidad']}")

            except:
                datos['caracteristicas'] = None
                datos['salario'] = None
                datos['experiencia'] = None
                datos['jornada'] = None
                datos['modalidad'] = None

            # 5. DESCRIPCIÓN COMPLETA - AQUÍ ESTÁ EL PROBLEMA PRINCIPAL
            try:
                # MÉTODO 1: Buscar el div que contiene los párrafos de descripción
                descripcion_container = driver.find_element(By.CSS_SELECTOR, "#description-full-details")

                # Buscar específicamente el div que viene DESPUÉS de .vacancy_features
                descripcion_div = descripcion_container.find_element(By.XPATH, ".//div[contains(@class, 'vacancy_features')]/following-sibling::div")

                # Extraer todos los párrafos
                paragrafos = descripcion_div.find_elements(By.TAG_NAME, "p")

                if paragrafos:
                    textos_descripcion = []
                    for p in paragrafos:
                        texto_p = self.limpiar_texto(p.text)
                        if texto_p:
                            textos_descripcion.append(texto_p)

                    datos['descripcion'] = ' '.join(textos_descripcion)
                    print(f"      ✓ Descripción: {len(datos['descripcion'])} caracteres")
                else:
                    # Fallback: tomar todo el texto del div
                    datos['descripcion'] = self.limpiar_texto(descripcion_div.text)
                    print(f"      ✓ Descripción (fallback): {len(datos['descripcion'])} caracteres")

            except:
                try:
                    # MÉTODO 2: Buscar directamente todos los párrafos dentro del contenedor
                    descripcion_container = driver.find_element(By.CSS_SELECTOR, "#description-full-details")
                    todos_paragrafos = descripcion_container.find_elements(By.TAG_NAME, "p")

                    if todos_paragrafos:
                        textos_descripcion = []
                        for p in todos_paragrafos:
                            texto_p = self.limpiar_texto(p.text)
                            if texto_p:
                                textos_descripcion.append(texto_p)

                        datos['descripcion'] = ' '.join(textos_descripcion)
                        print(f"      ✓ Descripción (método 2): {len(datos['descripcion'])} caracteres")
                    else:
                        datos['descripcion'] = None
                except:
                    try:
                        # MÉTODO 3: Selector más general
                        descripcion_elem = driver.find_element(By.CSS_SELECTOR, ".embedded_vacancy")
                        # Buscar solo los párrafos, excluyendo las características
                        paragrafos = descripcion_elem.find_elements(By.XPATH, ".//div[not(contains(@class, 'vacancy_features'))]//p")

                        if paragrafos:
                            textos_descripcion = []
                            for p in paragrafos:
                                texto_p = self.limpiar_texto(p.text)
                                if texto_p and len(texto_p) > 10:  # Filtrar textos muy cortos
                                    textos_descripcion.append(texto_p)

                            datos['descripcion'] = ' '.join(textos_descripcion)
                            print(f"      ✓ Descripción (método 3): {len(datos['descripcion'])} caracteres")
                        else:
                            datos['descripcion'] = None
                            print("      ✗ Descripción no encontrada")
                    except:
                        datos['descripcion'] = None
                        print("      ✗ Descripción no encontrada")

            # 6. FECHA DE PUBLICACIÓN
            try:
                # Buscar en las características
                fecha_elem = driver.find_element(By.XPATH, "//div[contains(@class, 'vacancy_feature') and (contains(text(), 'hace') or contains(text(), 'actualizado'))]")
                datos['fecha_publicacion'] = self.limpiar_texto(fecha_elem.text)
                print(f"      ✓ Fecha: {datos['fecha_publicacion']}")
            except:
                datos['fecha_publicacion'] = None

            # DEBUG: Si no se extrajo descripción, guardar HTML
            if not datos['descripcion'] or len(datos['descripcion']) < 50:
                print(f"      ⚠️  Descripción muy corta o vacía, guardando HTML para debug...")
                try:
                    with open(f'debug_descripcion_{index}.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                except:
                    pass

            return datos

        except Exception as e:
            print(f"      ❌ Error al extraer detalles: {e}")
            # Guardar HTML para debug
            try:
                with open(f'debug_accion_trabajo_{index}.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print(f"      💾 HTML guardado para debug: debug_accion_trabajo_{index}.html")
            except:
                pass
            return None

    def scrape_accion_trabajo(self, url, max_scrolls=15):
        """Scrapea trabajos de AcciónTrabajo"""
        driver = None
        resultados = []

        try:
            print(f"\n📄 Accediendo a: {url}")
            driver = self.iniciar_driver()
            driver.get(url)

            # Esperar carga inicial
            time.sleep(random.uniform(5, 8))

            # Verificar que la página cargó correctamente
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".results_page"))
                )
                print("   ✅ Página cargada correctamente")
            except TimeoutException:
                print("   ❌ Error: No se pudo cargar la página")
                return []

            # Hacer scroll para cargar todos los trabajos
            total_trabajos = self.scroll_para_cargar_trabajos(driver, max_scrolls)

            # Obtener lista de trabajos
            trabajos = driver.find_elements(By.CSS_SELECTOR, ".listing_url")
            print(f"\n   📋 Trabajos encontrados: {len(trabajos)}")

            if not trabajos:
                print("   ❌ No se encontraron trabajos")
                return []

            # Procesar cada trabajo
            for i, trabajo in enumerate(trabajos, 1):
                try:
                    print(f"\n   [{i}/{len(trabajos)}] Procesando trabajo {i}...")

                    # Scroll al trabajo para que sea visible
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trabajo)
                    time.sleep(1)

                    # Hacer clic en el trabajo
                    try:
                        trabajo.click()
                    except:
                        # Si falla, usar JavaScript
                        driver.execute_script("arguments[0].click();", trabajo)

                    print(f"      👆 Click en trabajo {i}")

                    # Esperar a que cargue el panel de detalles
                    time.sleep(3)

                    # Extraer detalles
                    datos = self.extraer_detalles_trabajo(driver, i)

                    if datos:
                        datos['index'] = i
                        resultados.append(datos)
                        print(f"      ✅ Trabajo {i} procesado exitosamente")
                    else:
                        print(f"      ⚠️  No se extrajeron datos del trabajo {i}")

                    # Pausa entre trabajos
                    time.sleep(random.uniform(2, 4))

                except Exception as e:
                    print(f"   ✗ Error en trabajo {i}: {e}")
                    # Capturar screenshot del error
                    try:
                        driver.save_screenshot(f'error_accion_trabajo_{i}.png')
                    except:
                        pass
                    continue

            print(f"\n🎯 RESUMEN FINAL:")
            print(f"   • Total trabajos encontrados: {len(trabajos)}")
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

    def guardar_resultados(self, jobs, filename='accion_trabajo_desarrolladores.csv'):
        """Guarda trabajos en CSV"""
        if jobs:
            df = pd.DataFrame(jobs)

            # Reordenar columnas
            columnas_orden = [
                'index', 'titulo', 'empresa', 'ubicacion', 'salario',
                'experiencia', 'jornada', 'modalidad', 'fecha_publicacion',
                'caracteristicas', 'descripcion'
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
            print(f"   Con salario: {df['salario'].notna().sum()}")
            print(f"   Con modalidad: {df['modalidad'].notna().sum()}")
            print(f"   Con descripción: {df['descripcion'].notna().sum()}")

        else:
            print("\n❌ No se encontraron trabajos para guardar")


def main():
    print("="*60)
    print("🚀 SCRAPER DE ACCIÓN TRABAJO - QA ECUADOR")  # CAMBIO 1: Título
    print("="*60)
    print("\n⚠️  ADVERTENCIAS:")
    print("   • Este script es EXPERIMENTAL")
    print("   • Solo para fines EDUCATIVOS")
    print("   • Puede fallar si cambia la estructura HTML\n")

    input("Presiona ENTER para continuar...")

    # CAMBIO 2: URL de AcciónTrabajo para QA
    url = "https://ec.acciontrabajo.com/buscar-empleos?q=Qa&l=Ecuador"

    scraper = AccionTrabajoScraper()

    # Scrapear con 15 scrolls (puedes ajustar este número)
    jobs = scraper.scrape_accion_trabajo(url, max_scrolls=15)

    # CAMBIO 3: Guardar resultados con nombre específico
    scraper.guardar_resultados(jobs, filename='accion_trabajo_qa.csv')

    print("\n" + "="*60)
    print("✅ PROCESO FINALIZADO")
    print("="*60)


if __name__ == "__main__":
    main()