import os
import json
import unicodedata
import re
from datetime import datetime

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
    if "Caja de cambios" in version:
        print(f"Campo encontrado: {version['Caja de cambios']}")  # Depuración para ver el contenido
        cajacambios = normalize_text(version["Caja de cambios"]).lower()
        if "manual" in cajacambios:
            version["Caja de cambios"] = "manual"
        else:
            version["Caja de cambios"] = "automatic"
    else:
        print(f"Claves disponibles en el JSON: {list(version.keys())}")  # Muestra todas las claves
        version["Caja de cambios"] = "unknown"
    return version.get("Caja de cambios", "unknown")
def process_version(version, brand, model, output_path):
    """
    Procesa una versión individual y guarda un archivo JSON con sus datos.
    """
    try:
        # Obtener nombre único para la versión
        version_name = version.get("name", "")  # Usar el nombre original aquí
        # Transformar el combustible directamente aquí
        fuel_type = transformar_combustible(version)
        gearbox_type = transformar_caja_de_cambios(version)
        file_name = f"{brand}_{model}_{version_name}_{gearbox_type}.json"
        file_path = os.path.join(output_path, file_name)
        # Crear datos para la versión
        current_year = datetime.now().year
        end_year = version.get("end_year", 0)
        if end_year == "":
            end_year = current_year
        print(f"El año final es: {end_year}")
        
        version_data = {
            "brand": brand,
            "model": model,
            "version_name": version_name,  # Usar el version_name limpio aquí
            "start_year": version.get("start_year", 0),
            "end_year": end_year,
            "keywords": version_name,
            "fuel_type": fuel_type,  # Combustible procesado
            "gearbox_type": gearbox_type,  # Caja de cambios procesada
            "potencia": version.get("potencia", 0)
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

def process_directory(input_dir, output_dir):
    """
    Recorre el directorio de entrada, procesa los archivos JSON y guarda los parámetros.
    """
    for root, _, files in os.walk(input_dir):
        # Obtener la ruta relativa para replicar la estructura
        relative_path = os.path.relpath(root, input_dir)
        output_path = os.path.join(output_dir, relative_path)
        
        # Crear directorio de salida si no existe
        os.makedirs(output_path, exist_ok=True)
        
        # Procesar cada archivo JSON
        brand = os.path.basename(root)  # Nombre del subdirectorio actual
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                
                # Procesar el archivo JSON
                process_json(file_path, brand, output_path)

if __name__ == "__main__":
    process_directory(input_dir, output_dir)
    print(f"Parámetros guardados en la carpeta '{output_dir}'")
