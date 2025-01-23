import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import os

# Función para guardar los datos en un archivo JSON
def save_to_json(base_path, data, brand, model, keywords,min_year, max_year, gearbox_types, engine_types):
    """
    Guarda los datos, incluyendo las especificaciones de búsqueda, en un archivo JSON.
    Crea una estructura de directorios basada en la marca y el modelo.
    """
    # Define la ruta completa para guardar el archivo
    brand_dir = os.path.join(base_path, "wallapop_ads", brand)
    model_dir = os.path.join(brand_dir, model)
    
    # Crea los directorios si no existen
    os.makedirs(model_dir, exist_ok=True)
    # Define el nombre del archivo (puedes ajustarlo según tu lógica)
    file_name = f"./{brand}_{model}_{keywords}-{min_year}-{max_year}_{gearbox_types}_{engine_types}_price_list_.json"
    file_path = os.path.join(model_dir, file_name)
    
    # Guarda los datos en formato JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Datos guardados en: {file_path}")
#Ignorar errores de SSL
def setup_driver():
    options = Options()
    options.add_argument("--ignore-certificate-errors")  # Ignorar errores de certificado
    options.add_argument("--ignore-ssl-errors=yes")      # Ignorar errores SSL
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")                  # Opcional: Modo sin ventana (para mayor velocidad)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# Función principal para obtener datos de Wallapop
def get_wallapop_car_data(driver,min_year, max_year, min_km, max_km, min_sale_price, max_sale_price, brand, model, latitude, longitude, keywords, gearbox_types, engine_types, max_horsepower, min_horsepower):
    base_url = "https://es.wallapop.com/app/search?"
    """gearbox_type_str = ','.join(gearbox_types)
    engine_types_str = ','.join(engine_types)"""
    # Convertir las listas de caja de cambios y motores en cadenas separadas por comas
    keywords_with_spaces = keywords.replace(" ", "%20")
    
    params = {
        'filters_source': 'default_filters',
        'keywords': "",
        'category_ids': '100',
        'latitude': latitude,
        'longitude': longitude,
        'order_by': 'price_high_to_low',
        'brand': brand,
        'model': model,
        'min_year': min_year,
        'max_year': max_year,
        'min_km': min_km,
        'max_km': max_km,
        'min_sale_price': min_sale_price,
        'max_sale_price': max_sale_price,
        'gearbox': gearbox_types,  # Filtros de tipo de caja de cambios (automático, manual)
        'engine': engine_types,
        'body_type': 'others,van,4X4,mini_van,small_car,coupe_cabrio,sedan,family_car',  # Tipos de carrocería
        'min_horse_power': min_horsepower, #Potencia minima
        'max_horse_power': max_horsepower #Potencia máxima
    }

    # Inicializamos una lista vacía para almacenar los anuncios
    car_data = []
    
    first_run = True  # Variable para indicar si es la primera ejecución
    
    while True:
        # Construir la URL con los parámetros actuales
        url = f"{base_url}engine={params['engine']}&min_horse_power={params['min_horse_power']}&max_horse_power={params['max_horse_power']}&min_year={params['min_year']}&max_year={params['max_year']}&min_km={params['min_km']}&max_km={params['max_km']}&min_sale_price={params['min_sale_price']}&max_sale_price={params['max_sale_price']}&gearbox={params['gearbox']}&brand={params['brand']}&model={params['model']}&filters_source={params['filters_source']}&keywords={params['keywords']}&category_ids=100&longitude={params['longitude']}&latitude={params['latitude']}&order_by=price_high_to_low"
        driver.get(url)
        # Iniciar el contador de tiempo
        start_time = time.time()
        # Espera prudencial para que la página cargue completamente antes de interactuar
        if first_run:
            time.sleep(2)  # Espera 2 segundos solo en la primera ejecución
            first_run = False  # Ya no es la primera ejecución después de la primera iteración

            # Aceptar el banner de cookies
            try:
                cookies_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                cookies_button.click()
                print("Cookies aceptadas.")
            except Exception as e:
                print(f"No se encontró el banner de cookies: {e}")

            # Intentar hacer clic en el botón "Saltar" 3 veces
            for _ in range(3):
                try:
                    shadow_host = WebDriverWait(driver, 10).until(
                         EC.presence_of_element_located((By.CSS_SELECTOR, "walla-button.TooltipWrapper__skip"))
                    )
                    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
                    if shadow_root:
                        skip_button = shadow_root.find_element(By.CSS_SELECTOR, "button.walla-button__button")
                        skip_button.click()
                        print("Clic en 'Saltar' realizado.")
                        time.sleep(1)  # Pausa después de cada clic
                except Exception as e:
                    print(f"Error al intentar hacer clic en 'Saltar': {e}")

        # 1. Bajar hasta el final de la página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Esperar para asegurarse de que la página se haya cargado completamente

        # 2. Buscar el botón 'Ver más productos' dentro del shadow DOM
        try:
            shadow_host = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "btn-load-more"))
            )
            shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)

            # Buscar el botón dentro del shadow root y hacer clic en él
            more_products_button = shadow_root.find_element(By.CSS_SELECTOR, "button.walla-button__button--primary")
            more_products_button.click()
            print("Clic en 'Ver más productos' realizado.")
            time.sleep(2)  # Esperar para cargar más productos
        except Exception as e:
            print(f"No se pudo hacer clic en 'Ver más productos' o no hay: {e}")

        # 3. Realizar scroll hacia el maximo posible
    
        last_position = driver.execute_script("return window.scrollY")  # Obtener la posición actual del scroll

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1 )  # Pausa para permitir que la página cargue

            new_position = driver.execute_script("return window.scrollY")  # Obtener la nueva posición del scroll

            # Si la posición no ha cambiado, significa que hemos llegado al final de la página
            if new_position == last_position:
                print("No hay más contenido para cargar, terminando el scroll.")
                break

            last_position = new_position  # Actualizar la última posición para la siguiente iteración

        # Extraer anuncios después de hacer el scroll
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.ItemCardList__item"))
            )
        except TimeoutException as e:
            print("Error: Tiempo de espera agotado. No se encontró el elemento.")
            print(e)
        cards = driver.find_elements(By.CSS_SELECTOR, "a.ItemCardList__item")
        
        # Si hay anuncios, extraemos los datos
        for card in cards:
            try:
                link = card.get_attribute("href")
                title = card.get_attribute("title")
                details = card.find_elements(By.CSS_SELECTOR, "div.ItemExtraInfo label.mb-0")
                
                # Intentamos obtener la descripción, si no existe, usamos una cadena vacía
                try:
                    description = card.find_element(By.CSS_SELECTOR, "span.ItemCardWide__description").text.strip()
                except:
                    description = ""  # Si no hay descripción, dejamos este campo vacío
                
                if len(details) >= 5:
                    # Procesar el precio y limpiar texto
                    price_text = card.find_element(By.CSS_SELECTOR, ".ItemCardWide__price").text.strip()
                    price_text = price_text.replace("€", "").replace(".", "").replace(",", "")  # Eliminamos comas y puntos
                    price = int(price_text) / 100  # Convertimos a número y dividimos entre 100

                    # Crear diccionario con la información del anuncio
                    car_info = {
                        "titulo": title,
                        "enlace": link,
                        "descripcion": description,  # Campo seguro incluso si no hay descripción
                        "combustible": details[0].text,  # Tipo de combustible
                        "cambio": details[1].text,  # Caja de cambios
                        "potencia": details[2].text,  # Potencia en CV
                        "año": details[3].text,  # Año matriculación
                        "kilómetros": details[4].text,  # Kms
                        "precio": price  # Precio
                    }

                    # Evitar duplicados
                    if car_info not in car_data:
                        car_data.append(car_info)
                        print(f"Anuncio extraído: {car_info}")
                else:
                    print("Detalles insuficientes para extraer los datos del coche.")
            except Exception as e:
                print(f"Error al procesar un anuncio: {e}")

        # Verificar si hay más páginas de resultados
        next_button = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Página siguiente']")
        if next_button:
            continue
        else:
            break
    # Obtener el tiempo total de ejecución
    end_time = time.time()  # Registrar el tiempo final
    elapsed_time = end_time - start_time  # Calcular el tiempo transcurrido

    print(f"Tiempo total de ejecución: {elapsed_time:.2f} segundos")
    # Obtener la fecha y hora actuales
    timestamp = datetime.now().strftime("%d-%m-%Y_%Hh_%Mm")
    base_path = "./wallapop_ads"
    output_path = f"./{brand}_{model}_{keywords}_price_list_{timestamp}.json"

    # Guardar los datos con la especificación de la búsqueda y fecha
    search_info = {
        "búsqueda": {
            "marca": brand,
            "modelo": model,
            "version": keywords,
            "año mínimo": min_year,
            "año máximo": max_year,
            "km mínimo": min_km,
            "km máximo": max_km,
            "precio mínimo": min_sale_price,
            "precio máximo": max_sale_price,
            "ubicación": {"latitud": latitude, "longitud": longitude},
            "tipos de cambio": gearbox_types,
            "tipos de motor": engine_types,
            "potencia máxima": max_horsepower,
            "potencia mínima": min_horsepower,
            "categoría": 'otros, furgoneta, 4X4, mini furgoneta, coche pequeño, coupé cabrio, sedán, coche familiar',
            "url": url
        },
        "anuncios": car_data
    }

    # Guardar todos los resultados acumulados en un solo JSON
    save_to_json(base_path, search_info, brand, model, keywords, min_year, max_year, gearbox_types, engine_types)
    print(f"Se extrajeron {len(car_data)} anuncios. Datos guardados en {output_path}")

    return car_data

#Parametros de busqueda
#min_year = 1940
#max_year = 2007
min_km = 2007
max_km = 300000
min_sale_price = 1
max_sale_price = 1000000
#keywords = ""  # Palabra clave externa
#gearbox_types = ['automatic', 'manual']
#engine_types = ['gasoline','gasoil','electric-hybrid','others']
#brand = "MINI"
#model = "MINI"  # Modelo en la URL
latitude = 40.578494
longitude = -3.892771
min_horsepower = 1
#max_horsepower = 1000
base_directory = 'parameters_scrapper'
for subdir, _, files in os.walk(base_directory):
    for file in files:
        if file.endswith('.json') and file.startswith('Audi'):
            file_path = os.path.join(subdir, file)
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                brand = data.get('brand', '')
                model = data.get('model', '')
                min_year = int(data.get('start_year', '1940'))
                max_year = int(data.get('end_year', '2025'))
                max_horsepower = int(data.get('potencia', '1000'))
                keywords = data.get('version_name', '')
                gearbox_types = data.get('gearbox_type', ['automatic', 'manual'])
                engine_types = data.get('fuel_type', ['gasoline','gasoil','electric-hybrid','others'])
                
                # Llamada a la función con los parámetros obtenidos del JSON
                get_wallapop_car_data(driver,min_year, max_year, min_km, max_km, min_sale_price, max_sale_price, brand, model, latitude, longitude, keywords, gearbox_types, engine_types, max_horsepower, min_horsepower)
driver.quit()