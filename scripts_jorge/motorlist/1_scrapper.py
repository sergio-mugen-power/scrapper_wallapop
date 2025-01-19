# Import Libraries
import requests
from bs4 import BeautifulSoup
import json
import re
import os


def get_engine_links(brand_url):
    # Obtengo los distintos links de los motores para una marca
    response = requests.get(brand_url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("h2", class_="entry-title")

    link_list = []
    for link in links:
        link = link.find("a")["href"]
        link_list.append(link)

    return link_list


def agregar_vinetas(web_page, final_text, texts):
    # Posibles viñetas
    try:
        vinetas = web_page.find("ul")
        vinetas_list = "\n".join(
            [f"- {li.get_text(strip=True)}" for li in vinetas.find_all("li")]
        )

        # Extraer las desventajas
        disadvantages = web_page.find(
            "h3", string=lambda text: "Disadvantages" in text if text else False
        ).find_next("ul")
        disadvantages_list = "\n".join(
            [f"- {li.get_text(strip=True)}" for li in disadvantages.find_all("li")]
        )

        for text in texts:
            final_text.append(text.get_text(strip=True))
        final_text = "".join(final_text) + vinetas_list + disadvantages_list
        final_text = final_text.replace("\n", " ")

    except:
        for text in texts:
            final_text.append(text.get_text(strip=True))
        final_text = "".join(final_text)

    return final_text


def revisar_fuelconsumption(table_rows):
    count = 0
    for row in table_rows:
        cells = row.find_all("td")
        key = cells[0].get_text(strip=True)
        if "Fuel consumption" in key:
            count += 1

    return count >= 2


def usar_fuelconsumption(key, value):
    """hay algunos casos donde existen varias filas de fuel consumption y no
    queremos sobreescribir ninguna sino quedarnos con todos los casos"""

    if "Fuel consumption" in key:
        key2 = value.get_text(strip=True, separator="\n").split("\n")[0]
        key = key + " " + key2
        value = "".join(value.get_text(strip=True, separator="\n").split("\n")[1:])
    else:
        value = value.get_text(strip=True)

    return key, value


def get_data(link_url):
    # Obtengo el cuerpo de la pagina
    response = requests.get(link_url)
    soup = BeautifulSoup(response.content, "html.parser")
    page = soup.find_all("div", class_="entry-content clear")

    # Obtengo el titulo del motor
    title = soup.find("h1", class_="entry-title").get_text(strip=True)

    # Obtengo el texto tanto la introducción como las desventajas
    final_text = []
    texts = page[0].find_all("p")
    # Posibles viñetas
    final_text = agregar_vinetas(web_page=page[0], final_text=final_text, texts=texts)

    # Obtengo los datos de la tabla y los transformo en un diccionario
    table = page[0].find("table")
    table_rows = table.find_all("tr")  # Todas las filas de la tabla

    table_data = {}
    prefix = ""  # Variable para almacenar la clave adicional de la fila especial

    # Esto es para revisar si existen varias filas de fuel consumption
    fuel_consumption_bool = revisar_fuelconsumption(table_rows)

    for row in table_rows:
        cells = row.find_all("td")

        if len(cells) == 1 and "colspan" in cells[0].attrs:  # Detecto fila especial
            prefix = cells[0].get_text(strip=True)  # Actualizo el prefijo
            continue
        elif len(cells) == 2:  # Fila estándar
            key = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            if prefix:
                key = f"{prefix}_{key}"  # Concateno el prefijo si existe

        # Este es un condicional ya que hay algunos casos donde existen varios tipos de fuel consumption
        # Value tiene que ser cells[1] ya que necesito hacer un strip diferente
        if fuel_consumption_bool:
            key, value = usar_fuelconsumption(key=key, value=cells[1])

        table_data[key] = value

    table_data["title"] = title
    table_data["description"] = final_text

    return table_data


urls = [
    "https://mymotorlist.com/engines/bmw/",
    "https://mymotorlist.com/engines/mercedes/",
    "https://mymotorlist.com/engines/alfa-romeo/",
    "https://mymotorlist.com/engines/audi/",
    "https://mymotorlist.com/engines/chevrolet/",
    "https://mymotorlist.com/engines/chrysler/",
    "https://mymotorlist.com/engines/daewoo/",
    "https://mymotorlist.com/engines/dodge/",
    "https://mymotorlist.com/engines/fiat/",
    "https://mymotorlist.com/engines/ford/",
    "https://mymotorlist.com/engines/honda/",
    "https://mymotorlist.com/engines/hyundai/",
    "https://mymotorlist.com/engines/infiniti/",
    "https://mymotorlist.com/engines/isuzu/",
    "https://mymotorlist.com/engines/jaguar/",
    "https://mymotorlist.com/engines/jeep/",
    "https://mymotorlist.com/engines/kia/",
    "https://mymotorlist.com/engines/land-rover/",
    "https://mymotorlist.com/engines/lexus/",
    "https://mymotorlist.com/engines/man/",
    "https://mymotorlist.com/engines/mazda/",
    "https://mymotorlist.com/engines/mini/",
    "https://mymotorlist.com/engines/mitsubishi/",
    "https://mymotorlist.com/engines/opel/",
    "https://mymotorlist.com/engines/peugeot/",
    "https://mymotorlist.com/engines/porsche/",
    "https://mymotorlist.com/engines/renault/",
    "https://mymotorlist.com/engines/rover/",
    "https://mymotorlist.com/engines/saab/",
    "https://mymotorlist.com/engines/ssangyong/",
    "https://mymotorlist.com/engines/subaru/",
    "https://mymotorlist.com/engines/suzuki/",
    "https://mymotorlist.com/engines/toyota/",
    "https://mymotorlist.com/engines/volkswagen/",
    "https://mymotorlist.com/engines/volvo/",
    "https://mymotorlist.com/engines/nissan/",
]

# Obtengo el directorio correcto
current_path = os.getcwd()
parent_dir = os.path.abspath(os.path.join(current_path, os.pardir))
landing_folder = os.path.join(current_path, "datasets", "motorlist", "1_landing")


for url in urls:
    links = get_engine_links(url)
    data = []
    for link in links:
        table_data = get_data(link)
        data.append(table_data)

        # Guardar cada diccionario como un archivo JSON usando el campo "title"
    for item in data:
        title = item.get(
            "title", "untitled"
        )  # Toma el campo "title" o usa "untitled" si no existe
        # Limpia el título para usarlo como nombre de archivo
        safe_title = re.sub(
            r'[\\/:"*?<>|]+', "_", title
        )  # Reemplaza caracteres no permitidos
        filename = f"{safe_title}.json"
        filename = os.path.join(landing_folder, filename)

        # Guarda el diccionario en un archivo JSON
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(item, f, ensure_ascii=False, indent=4)

    print(url)
    print("Archivos JSON generados correctamente.")
