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

class OpcionEmpleoAnalisterScraper:
    def __init__(self):
        self.base_url = "https://www.opcionempleo.ec"
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]

        # Lista que se llenará con las URLs encontradas
        self.urls_trabajos = []

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

    def recolectar_urls_trabajos(self, driver, url_inicial):
        """PASO 1: Recolecta todas las URLs de trabajos navegando por páginas"""
        print(f"\n🔍 FASE 1: RECOLECTANDO URLs DE TRABAJOS")
        print("="*60)

        urls_encontradas = []
        pagina_actual = 1
        max_paginas = 20  # Límite de seguridad

        try:
            # Ir a la página inicial
            print(f"📄 Accediendo a: {url_inicial}")
            driver.get(url_inicial)
            time.sleep(random.uniform(4, 7))

            while pagina_actual <= max_paginas:
                print(f"\n📋 PÁGINA {pagina_actual}")
                print("-" * 40)

                try:
                    # DEBUG: Guardar HTML de las primeras páginas
                    if pagina_actual <= 3:
                        try:
                            with open(f'debug_pagina_{pagina_actual}.html', 'w', encoding='utf-8') as f:
                                f.write(driver.page_source)
                            print(f"   💾 HTML guardado: debug_pagina_{pagina_actual}.html")
                        except:
                            pass

                    # SELECTORES CORREGIDOS basados en el HTML
                    selectores_trabajos = [
                        "article.job a[href*='/jobad/']",  # Selector principal del HTML
                        ".job a[href*='/jobad/']",
                        ".jobs li a[href*='/jobad/']",
                        "a[href*='/jobad/']"  # Cualquier enlace con jobad
                    ]

                    trabajos_en_pagina = []

                    # Probar diferentes selectores
                    for selector in selectores_trabajos:
                        try:
                            elementos = driver.find_elements(By.CSS_SELECTOR, selector)
                            if elementos:
                                trabajos_en_pagina = elementos
                                print(f"   ✓ Selector funcionó: {selector}")
                                break
                        except:
                            continue

                    if not trabajos_en_pagina:
                        print(f"   ⚠️  No se encontraron trabajos con ningún selector")
                        print(f"   🔍 Buscando cualquier enlace con 'jobad'...")

                        # Último intento: buscar por href que contenga jobad
                        try:
                            todos_links = driver.find_elements(By.TAG_NAME, "a")
                            for link in todos_links:
                                href = link.get_attribute('href')
                                if href and '/jobad/' in href:
                                    trabajos_en_pagina.append(link)

                            if trabajos_en_pagina:
                                print(f"   ✓ Encontrados {len(trabajos_en_pagina)} enlaces con 'jobad'")
                        except Exception as e:
                            print(f"   ❌ Error buscando enlaces: {e}")

                    # Extraer URLs únicas
                    urls_pagina = []
                    for trabajo in trabajos_en_pagina:
                        try:
                            href = trabajo.get_attribute('href')
                            if href and href not in urls_encontradas and '/jobad/' in href:
                                urls_encontradas.append(href)
                                urls_pagina.append(href)
                        except:
                            continue

                    print(f"   ✓ Trabajos encontrados en página {pagina_actual}: {len(urls_pagina)}")
                    print(f"   📊 Total acumulado: {len(urls_encontradas)} URLs")

                    # Si no encontró trabajos en la primera página, es un problema
                    if pagina_actual == 1 and len(urls_pagina) == 0:
                        print(f"   ❌ No se encontraron trabajos en la primera página")
                        break

                    # ===== BUSCAR BOTÓN "SIGUIENTE PÁGINA" CORREGIDO =====
                    boton_siguiente = None
                    try:
                        print(f"   🔍 Buscando botón 'Siguiente página'...")

                        # 1. SELECTOR ESPECÍFICO del HTML que me pasaste
                        try:
                            boton_siguiente = driver.find_element(By.CSS_SELECTOR,
                                "button[data-name='p'].next, .ves-control.ves-add.next")
                            if boton_siguiente.is_displayed() and boton_siguiente.is_enabled():
                                print(f"   ✓ Botón siguiente encontrado con selector específico")
                            else:
                                boton_siguiente = None
                        except:
                            pass

                        # 2. SELECTOR POR CLASE "next"
                        if not boton_siguiente:
                            try:
                                boton_siguiente = driver.find_element(By.CSS_SELECTOR, ".next")
                                if boton_siguiente.is_displayed() and boton_siguiente.is_enabled():
                                    print(f"   ✓ Botón siguiente encontrado con clase 'next'")
                                else:
                                    boton_siguiente = None
                            except:
                                pass

                        # 3. SELECTOR EN CONTENEDOR ".more"
                        if not boton_siguiente:
                            try:
                                boton_siguiente = driver.find_element(By.CSS_SELECTOR, ".more button")
                                if boton_siguiente.is_displayed() and boton_siguiente.is_enabled():
                                    print(f"   ✓ Botón siguiente encontrado en '.more'")
                                else:
                                    boton_siguiente = None
                            except:
                                pass

                        # 4. BUSCAR POR TEXTO "Siguiente página"
                        if not boton_siguiente:
                            try:
                                botones = driver.find_elements(By.TAG_NAME, "button")
                                for boton in botones:
                                    texto = boton.text.lower().strip()
                                    if 'siguiente página' in texto or 'siguiente' in texto:
                                        if boton.is_displayed() and boton.is_enabled():
                                            boton_siguiente = boton
                                            print(f"   ✓ Botón siguiente encontrado por texto: '{texto}'")
                                            break
                            except:
                                pass

                        # 5. ÚLTIMO INTENTO: Buscar enlaces con "siguiente"
                        if not boton_siguiente:
                            try:
                                enlaces = driver.find_elements(By.TAG_NAME, "a")
                                for enlace in enlaces:
                                    texto = enlace.text.lower().strip()
                                    if 'siguiente' in texto or 'next' in texto:
                                        if enlace.is_displayed() and enlace.is_enabled():
                                            boton_siguiente = enlace
                                            print(f"   ✓ Enlace siguiente encontrado: '{texto}'")
                                            break
                            except:
                                pass

                    except Exception as e:
                        print(f"   ⚠️  Error buscando botón siguiente: {e}")

                    # Si encontró el botón, hacer clic
                    if boton_siguiente:
                        print(f"   ▶️  Navegando a página {pagina_actual + 1}...")

                        # Scroll al botón
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_siguiente)
                            time.sleep(1)
                            print(f"   📍 Scroll realizado al botón")
                        except:
                            pass

                        # Hacer clic
                        try:
                            # Primer intento: Click normal
                            boton_siguiente.click()
                            print(f"   👆 Click normal realizado")
                        except:
                            try:
                                # Segundo intento: JavaScript click
                                driver.execute_script("arguments[0].click();", boton_siguiente)
                                print(f"   👆 Click JavaScript realizado")
                            except:
                                try:
                                    # Tercer intento: Simular evento
                                    driver.execute_script("""
                                        var event = new MouseEvent('click', {
                                            view: window,
                                            bubbles: true,
                                            cancelable: true
                                        });
                                        arguments[0].dispatchEvent(event);
                                    """, boton_siguiente)
                                    print(f"   👆 Click por evento simulado")
                                except Exception as e:
                                    print(f"   ❌ No se pudo hacer click: {e}")
                                    break

                        # Esperar a que cargue la nueva página
                        print(f"   ⏳ Esperando carga de página {pagina_actual + 1}...")
                        time.sleep(random.uniform(4, 7))

                        # Verificar que cambió la página
                        try:
                            # Buscar indicador de página actual
                            nuevos_trabajos = driver.find_elements(By.CSS_SELECTOR, "article.job a[href*='/jobad/']")
                            if len(nuevos_trabajos) > 0:
                                print(f"   ✅ Nueva página cargada con {len(nuevos_trabajos)} trabajos")
                                pagina_actual += 1
                            else:
                                print(f"   ⚠️  No se detectaron nuevos trabajos tras el click")
                                break
                        except:
                            print(f"   ⚠️  No se pudo verificar la nueva página")
                            pagina_actual += 1

                    else:
                        print(f"   🏁 No hay más páginas. Fin de la recolección.")
                        break

                except Exception as e:
                    print(f"   ❌ Error en página {pagina_actual}: {e}")
                    import traceback
                    traceback.print_exc()

                    # Guardar HTML de error
                    try:
                        with open(f'debug_error_pagina_{pagina_actual}.html', 'w', encoding='utf-8') as f:
                            f.write(driver.page_source)
                        print(f"   💾 HTML de error guardado: debug_error_pagina_{pagina_actual}.html")
                    except:
                        pass
                    break

            print(f"\n🎯 RECOLECCIÓN COMPLETADA:")
            print(f"   • Páginas navegadas: {pagina_actual}")
            print(f"   • URLs recolectadas: {len(urls_encontradas)}")

            return urls_encontradas

        except Exception as e:
            print(f"❌ Error general en recolección: {e}")
            import traceback
            traceback.print_exc()
            return urls_encontradas

    def limpiar_texto(self, texto):
        """Limpia texto eliminando espacios extra y caracteres especiales"""
        if not texto:
            return None
        # Reemplazar <span class="br"></span> y <br> con espacios
        texto_limpio = re.sub(r'<span class="br"></span>|<br\s*/?>|<b>|</b>', ' ', texto)
        # Limpiar espacios múltiples
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
        return texto_limpio if texto_limpio else None

    def extraer_detalles_trabajo(self, driver, index, url):
        """PASO 2: Extrae detalles del trabajo actual (igual que antes)"""
        try:
            # Esperar a que cargue la página
            time.sleep(3)

            datos = {'url': url}

            # 1. TÍTULO del trabajo
            try:
                titulo_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
                )
                datos['titulo'] = self.limpiar_texto(titulo_elem.text)
                print(f"      ✓ Título: {datos['titulo']}")
            except:
                datos['titulo'] = None
                print("      ✗ Título no encontrado")

            # 2. EMPRESA
            try:
                empresa_elem = driver.find_element(By.CSS_SELECTOR, ".company a")
                datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                print(f"      ✓ Empresa: {datos['empresa']}")
            except:
                try:
                    empresa_elem = driver.find_element(By.CSS_SELECTOR, ".company")
                    datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                    print(f"      ✓ Empresa: {datos['empresa']}")
                except:
                    try:
                        empresa_elem = driver.find_element(By.CSS_SELECTOR, "p.company")
                        datos['empresa'] = self.limpiar_texto(empresa_elem.text)
                        print(f"      ✓ Empresa: {datos['empresa']}")
                    except:
                        datos['empresa'] = None
                        print("      ✗ Empresa no encontrada")

            # 3. UBICACIÓN
            try:
                ubicacion_elem = driver.find_element(By.CSS_SELECTOR, ".details li span")
                datos['ubicacion'] = self.limpiar_texto(ubicacion_elem.text)
                print(f"      ✓ Ubicación: {datos['ubicacion']}")
            except:
                try:
                    detalles = driver.find_elements(By.CSS_SELECTOR, ".details li")
                    for detalle in detalles:
                        texto = detalle.text.strip()
                        if any(palabra in texto.lower() for palabra in ['quito', 'guayaquil', 'ecuador', 'pichincha', 'guayas', 'cuenca', 'azuay']):
                            datos['ubicacion'] = texto
                            print(f"      ✓ Ubicación: {datos['ubicacion']}")
                            break
                    else:
                        if detalles:
                            datos['ubicacion'] = detalles[0].text.strip()
                            print(f"      ✓ Ubicación (primer detalle): {datos['ubicacion']}")
                        else:
                            datos['ubicacion'] = None
                except:
                    datos['ubicacion'] = None

            # 4. DETALLES ADICIONALES (Modalidad, Jornada, etc.)
            try:
                detalles_list = driver.find_elements(By.CSS_SELECTOR, ".details li")
                datos['modalidad'] = None
                datos['jornada'] = None
                datos['tipo_contrato'] = None

                for detalle in detalles_list:
                    texto = detalle.text.lower()

                    if any(word in texto for word in ['remoto', 'presencial', 'híbrido', 'teletrabajo', 'casa', 'oficina']):
                        datos['modalidad'] = detalle.text.strip()

                    if any(word in texto for word in ['tiempo completo', 'tiempo parcial', 'medio tiempo', 'full time', 'part time', 'jornada']):
                        datos['jornada'] = detalle.text.strip()

                    if any(word in texto for word in ['permanente', 'temporal', 'contrato', 'indefinido', 'fijo']):
                        datos['tipo_contrato'] = detalle.text.strip()

                if datos['modalidad']:
                    print(f"      ✓ Modalidad: {datos['modalidad']}")
                if datos['jornada']:
                    print(f"      ✓ Jornada: {datos['jornada']}")
                if datos['tipo_contrato']:
                    print(f"      ✓ Tipo contrato: {datos['tipo_contrato']}")

            except:
                datos['modalidad'] = None
                datos['jornada'] = None
                datos['tipo_contrato'] = None

            # 5. FECHA DE PUBLICACIÓN
            try:
                fecha_elem = driver.find_element(By.CSS_SELECTOR, ".tags .badge")
                datos['fecha_publicacion'] = self.limpiar_texto(fecha_elem.text)
                print(f"      ✓ Fecha: {datos['fecha_publicacion']}")
            except:
                try:
                    fecha_elem = driver.find_element(By.CSS_SELECTOR, ".date, .published")
                    datos['fecha_publicacion'] = self.limpiar_texto(fecha_elem.text)
                    print(f"      ✓ Fecha: {datos['fecha_publicacion']}")
                except:
                    datos['fecha_publicacion'] = None

            # 6. DESCRIPCIÓN COMPLETA
            try:
                descripcion_elem = driver.find_element(By.CSS_SELECTOR, ".content")
                descripcion_html = descripcion_elem.get_attribute('innerHTML')
                datos['descripcion'] = self.limpiar_texto(descripcion_html)
                print(f"      ✓ Descripción: {len(datos['descripcion'])} caracteres")
            except:
                try:
                    descripcion_elem = driver.find_element(By.CSS_SELECTOR, "section.content")
                    descripcion_html = descripcion_elem.get_attribute('innerHTML')
                    datos['descripcion'] = self.limpiar_texto(descripcion_html)
                    print(f"      ✓ Descripción: {len(datos['descripcion'])} caracteres")
                except:
                    try:
                        contenido_elems = driver.find_elements(By.TAG_NAME, "p")
                        textos = []
                        for elem in contenido_elems:
                            texto = elem.text.strip()
                            if len(texto) > 50:
                                textos.append(texto)

                        if textos:
                            datos['descripcion'] = ' '.join(textos)
                            print(f"      ✓ Descripción (párrafos): {len(datos['descripcion'])} caracteres")
                        else:
                            datos['descripcion'] = None
                            print("      ✗ Descripción no encontrada")
                    except:
                        datos['descripcion'] = None
                        print("      ✗ Descripción no encontrada")

            # 7. SALARIO
            try:
                if datos['descripcion']:
                    desc_lower = datos['descripcion'].lower()
                    salario_patterns = [
                        r'\$\s*\d+[\d,]*(?:\.\d+)?',
                        r'\d+[\d,]*\s*usd',
                        r'salario[:\s]+\$?\s*\d+',
                        r'\d+\s*a\s*\d+\s*usd',
                    ]

                    for pattern in salario_patterns:
                        match = re.search(pattern, desc_lower)
                        if match:
                            datos['salario'] = match.group()
                            print(f"      ✓ Salario: {datos['salario']}")
                            break
                    else:
                        datos['salario'] = None
                else:
                    datos['salario'] = None
            except:
                datos['salario'] = None

            return datos

        except Exception as e:
            print(f"      ❌ Error al extraer detalles: {e}")
            return None

    def scrape_analista_datos_completo(self, url_inicial):
        """PROCESO COMPLETO: Recolectar URLs y extraer datos"""
        driver = None
        resultados = []

        try:
            driver = self.iniciar_driver()

            # FASE 1: Recolectar todas las URLs
            self.urls_trabajos = self.recolectar_urls_trabajos(driver, url_inicial)

            if not self.urls_trabajos:
                print("❌ No se encontraron URLs de trabajos")
                return []

            print(f"\n📄 GUARDANDO LISTA DE URLs...")
            with open('urls_analista_datos.txt', 'w', encoding='utf-8') as f:
                for i, url in enumerate(self.urls_trabajos, 1):
                    f.write(f"{i}. {url}\n")
            print(f"💾 Lista guardada en: urls_analista_datos.txt")

            # FASE 2: Extraer datos de cada trabajo
            print(f"\n🚀 FASE 2: EXTRAYENDO DATOS DE CADA TRABAJO")
            print("="*60)

            for index, url in enumerate(self.urls_trabajos, 1):
                print(f"\n{'='*60}")
                print(f"📋 TRABAJO {index}/{len(self.urls_trabajos)}")
                print(f"{'='*60}")
                print(f"📄 URL: {url}")

                try:
                    # Ir a la URL del trabajo
                    driver.get(url)
                    time.sleep(random.uniform(3, 6))

                    # Verificar que la página cargó
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".container"))
                        )
                        print("   ✅ Página cargada correctamente")
                    except TimeoutException:
                        print("   ❌ Error: Timeout al cargar la página")
                        continue

                    # Extraer detalles
                    print(f"   📝 Extrayendo información del trabajo {index}...")
                    datos = self.extraer_detalles_trabajo(driver, index, url)

                    if datos:
                        datos['index'] = index
                        resultados.append(datos)
                        print(f"      ✅ Trabajo {index} procesado exitosamente")
                    else:
                        print(f"      ⚠️  No se extrajeron datos del trabajo {index}")

                    # Pausa entre trabajos
                    if index < len(self.urls_trabajos):
                        pausa = random.uniform(2, 5)
                        print(f"   ⏸️  Pausando {pausa:.1f}s antes del siguiente trabajo...")
                        time.sleep(pausa)

                except Exception as e:
                    print(f"   ✗ Error en trabajo {index}: {e}")
                    try:
                        driver.save_screenshot(f'error_analista_{index}.png')
                        print(f"   📸 Screenshot guardado: error_analista_{index}.png")
                    except:
                        pass
                    continue

            print(f"\n🎯 RESUMEN FINAL:")
            print(f"   • URLs recolectadas: {len(self.urls_trabajos)}")
            print(f"   • Trabajos procesados: {len(resultados)}")
            print(f"   • Tasa de éxito: {len(resultados)/len(self.urls_trabajos)*100:.1f}%")

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

    def guardar_resultados(self, jobs, filename='opcion_empleo_analista_datos.csv'):
        """Guarda trabajos en CSV"""
        if jobs:
            df = pd.DataFrame(jobs)

            # Reordenar columnas
            columnas_orden = [
                'index', 'titulo', 'empresa', 'ubicacion', 'salario',
                'modalidad', 'jornada', 'tipo_contrato', 'fecha_publicacion',
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
            print(f"   Con salario: {df['salario'].notna().sum()}")
            print(f"   Con modalidad: {df['modalidad'].notna().sum()}")
            print(f"   Con descripción: {df['descripcion'].notna().sum()}")

        else:
            print("\n❌ No se encontraron trabajos para guardar")


def main():
    print("="*60)
    print("🚀 SCRAPER DE OPCIÓN EMPLEO - QA")  # CAMBIO 1: Título
    print("="*60)
    print("\n📋 INFORMACIÓN:")
    print("   • Navegará por páginas usando 'Siguiente'")
    print("   • Recolectará ~77 URLs de trabajos")  # CAMBIO 2: Cantidad esperada
    print("   • Visitará cada URL para extraer datos")
    print("   • Solo para fines EDUCATIVOS")
    print("   • Tiempo estimado: ~10-15 minutos")  # CAMBIO 3: Tiempo ajustado
    print("   • Con pausas para evitar detección\n")

    input("Presiona ENTER para continuar...")

    # CAMBIO 4: URL de búsqueda de QA
    url_inicial = "https://www.opcionempleo.ec/trabajo?s=qa&l=Ecuador"

    scraper = OpcionEmpleoAnalisterScraper()

    # Proceso completo: recolectar URLs y extraer datos
    jobs = scraper.scrape_analista_datos_completo(url_inicial)

    # CAMBIO 5: Nombre del archivo de salida
    scraper.guardar_resultados(jobs, filename='opcion_empleo_qa.csv')

    print("\n" + "="*60)
    print("✅ PROCESO FINALIZADO")
    print("="*60)


if __name__ == "__main__":
    main()