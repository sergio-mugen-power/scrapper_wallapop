import os
import json

# Directorios base
input_dir = "transformed_data"
output_dir = "parameters_scrapper"

# Crear directorio de salida si no existe
os.makedirs(output_dir, exist_ok=True)

def process_json(file_path, brand):
    """
    Procesa un archivo JSON para extraer los parámetros necesarios.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Extraer datos
        model = data.get("name")
        versions = data.get("versions", [])
        
        # Extraer años y keywords de las versiones
        min_year = min(v.get("start_year", 0) for v in versions)
        max_year = max(v.get("end_year", 0) for v in versions)
        keywords = [v.get("name", "") for v in versions]
        
        # Construir estructura de parámetros
        return {
            "brand": brand,
            "model": model,
            "min_year": min_year,
            "max_year": max_year,
            "keywords": keywords
        }
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return None

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
                output_file = os.path.join(output_path, file)
                
                # Procesar el archivo JSON
                parameters = process_json(file_path, brand)
                if parameters:
                    # Guardar parámetros en JSON
                    with open(output_file, 'w') as out_file:
                        json.dump(parameters, out_file, indent=4)

if __name__ == "__main__":
    process_directory(input_dir, output_dir)
    print(f"Parámetros guardados en la carpeta '{output_dir}'")
