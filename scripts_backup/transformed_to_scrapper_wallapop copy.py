import os
import json
import unicodedata
# Directorios base
input_dir = "transformed_data"
output_dir = "parameters_scrapper"

# Crear directorio de salida si no existe
os.makedirs(output_dir, exist_ok=True)

def normalize_text(text):
    """
    Normaliza el texto para eliminar inconsistencias en caracteres con acentos.
    """
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

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

    return version.get('Combustible', 'unknown')
def process_version(version, brand, model, output_path):
    """
    Procesa una versión individual y guarda un archivo JSON con sus datos.
    """
    try:
        # Obtener nombre único para la versión
        version_name = version.get("name", "unknown_version").replace(" ", "_")
        file_name = f"{brand}_{model}_{version_name}.json"
        file_path = os.path.join(output_path, file_name)

        # Transformar el combustible directamente aquí
        fuel_type = transformar_combustible(version)

        # Crear datos para la versión
        version_data = {
            "brand": brand,
            "model": model,
            "version_name": version.get("name", ""),
            "start_year": version.get("start_year", 0),
            "end_year": version.get("end_year", 0),
            "keywords": version.get("name", ""),
            "fuel_type": fuel_type  # Combustible procesado
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
        model = data.get("name", "unknown_model").replace(" ", "_")
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
