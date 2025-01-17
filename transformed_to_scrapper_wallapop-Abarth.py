import os
import json
import unicodedata
import re

# Directorios base
input_dir = "transformed_data"
output_dir = "parameters_scrapper"

def limpiar_version_name(version_name):
    """
    Filtra y limpia el nombre de la versión eliminando los números antes de 'CV', el texto entre paréntesis,
    las palabras que indican transmisión automática (como 'Aut', 'Automático', 'Auto', 'Secuencial')
    y los puntos y espacios desde un carácter hasta el final.
    """
    # Eliminar cualquier número antes de 'CV' y los textos entre paréntesis
    version_name = re.sub(r'\s*\d+\s*CV', ' CV', version_name)  # Elimina números antes de CV
    version_name = re.sub(r'\s*\(.*?\)', '', version_name)  # Elimina el texto entre paréntesis
    
    # Eliminar palabras relacionadas con la transmisión automática
    version_name = re.sub(r'\b(Aut|Automático|Auto|Secuencial|Multiair|S-Tronic|T-Jet)\b', '', version_name, flags=re.IGNORECASE)  # Elimina palabras de transmisión automática

    # Eliminar los puntos después de palabras como "Aut", "Auto", etc.
    version_name = re.sub(r'\b(Aut|Auto|Automático|Secuencial)\s*\.*', '', version_name, flags=re.IGNORECASE)  # Eliminar el punto después de las palabras

    # Eliminar puntos al final de la cadena o cualquier punto dentro de la cadena que quede.
    version_name = re.sub(r'\s*\.$', '', version_name)  # Elimina el punto al final de la cadena

    return version_name.strip()
# Crear directorio de salida si no existe
os.makedirs(output_dir, exist_ok=True)

def normalize_text(text):
    """
    Normaliza el texto para eliminar inconsistencias en caracteres con acentos.
    """
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii').strip()


def transformar_combustible(version):
    """
    Transforma el tipo de combustible según las reglas especificadas para una versión.
    """
    if 'Combustible' in version:
        combustible = normalize_text(version['Combustible'])  # Normalizar el texto
        if 'Gasolina' in combustible:
            version['Combustible'] = 'gasoline'
        elif 'Gasoleo' in combustible:  # Nota: 'Gasoleo' después de normalizar
            version['Combustible'] = 'gasoil'

    if 'Distintivo ambiental DGT' in version:
        distintivo = normalize_text(version['Distintivo ambiental DGT'])  # Normalizar
        if '0 emisiones' in distintivo or 'ECO' in distintivo:
            version['Combustible'] = 'electric-hybrid'

    return version.get('Combustible', '')

def transformar_caja_de_cambios(version):
    """
    Transforma el valor de la caja de cambios y lo clasifica como 'manual' o 'automatic'.
    """

    
    # Verificar si existe la clave "Caja de cambios"
    if "Caja de cambios" in version:
        print(f"Campo encontrado: {version['Caja de cambios']}")  # Depuración para ver el contenido
        cajacambios = version["Caja de cambios"].strip().lower()  # Normaliza el texto para comparar
        if "manual" in cajacambios:
            version["Caja de cambios"] = "manual"
        else:
            version["Caja de cambios"] = "automatic"
    else:
        # Si no existe la clave, asignar un valor predeterminado
        print("Clave 'Caja de cambios' no encontrada en el JSON.")
        version["Caja de cambios"] = "unknown"
    
    return version.get("Caja de cambios", "unknown")



def process_version(version, brand, model, output_path):
    """
    Procesa una versión individual y guarda un archivo JSON con sus datos.
    """
    try:
        # Obtener nombre único para la versión
        version_name_sin_limpiar = version.get("name", "unknown_version")
        version_name = limpiar_version_name(version_name_sin_limpiar)  # Limpiar el nombre de la versión
        gearbox_type = transformar_caja_de_cambios(version)
        file_name = f"{brand}_{model}_{version_name}_{gearbox_type}.json"
        file_path = os.path.join(output_path, file_name)

        # Transformar el combustible directamente aquí
        fuel_type = transformar_combustible(version)
        

        # Crear datos para la versión
        version_data = {
            "brand": brand,
            "model": model,
            "version_name": version_name,  # Usar el version_name limpio aquí
            "start_year": version.get("start_year", 0),
            "end_year": version.get("end_year", 0),
            "keywords": version_name,
            "fuel_type": fuel_type,  # Combustible procesado
            "gearbox_type": gearbox_type  # Caja de cambios procesada
            "potencia": version.get("")
        }

        # Guardar la versión como JSON
        with open(file_path, 'w', encoding='utf-8') as out_file:
            json.dump(version_data, out_file, indent=4)

        print(f"Guardado: {file_path}")
    except Exception as e:
        print(f"Error procesando versión: {e}")

def process_json(file_path, brand, output_path):
    """
    Procesa un archivo JSON para extraer las versiones y guardar archivos por cada una.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Obtener modelo y versiones
        model = data.get("name", "unknown_model")
        versions = data.get("versions", [])

        # Procesar cada versión
        for version in versions:
            process_version(version, brand, model, output_path)
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")

def process_abarth_directories(base_directory):
    for subdir, _, files in os.walk(base_directory):
        # Verificar si "abarth" está en el nombre del directorio
        if "abarth" in os.path.basename(subdir).lower():  # Convertir a minúsculas para una comparación case-insensitive
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(subdir, file)
                    with open(file_path, 'r', encoding='utf-8') as json_file:
                        data = json.load(json_file)
                        brand = data.get('brand', '')
                        model = data.get('model', '')
                        min_year = int(data.get('start_year', '1940'))
                        max_year = int(data.get('end_year', '2025'))
                        max_horsepower = int(data.get('potencia', '1000'))

                        # Llamada a la función con los parámetros obtenidos del JSON
                        get_wallapop_car_data(
                            min_year, max_year, min_km, max_km, 
                            min_sale_price, max_sale_price, brand, model, 
                            latitude, longitude, keywords, gearbox_types, 
                            engine_types, max_horsepower, min_horsepower
                        )

if __name__ == "__main__":
    process_abarth_directories(input_dir, output_dir)
    print(f"Parámetros guardados en la carpeta '{output_dir}'")

