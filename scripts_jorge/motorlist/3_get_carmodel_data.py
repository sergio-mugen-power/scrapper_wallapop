# Importar librerias y definir rutas

import json
import os
import pandas as pd
import numpy as np
import re
from openai import OpenAI
from dotenv import load_dotenv
import ast
import time

current_dir = os.getcwd()
parent_dir = os.path.join(current_dir, os.pardir, os.pardir)
parent_dir = os.path.abspath(parent_dir)

bronze_dir = os.path.join(parent_dir, "datasets", "motorlist", "2_bronze")
bronze_files = os.listdir(bronze_dir)
silver_dir = os.path.join(parent_dir, "datasets", "motorlist", "3_silver")
silver_files = os.listdir(silver_dir)

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la clave de API desde las variables de entorno
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


# Definir funciones para extraer información de coches y años
def extract_car_info(description):
    """Envía la descripción al modelo para extraer información sobre coches y años."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Puedes cambiar el modelo según lo que necesites
            messages=[
                {
                    "role": "system",
                    "content": "Extract car models and years from descriptions. Return them as a list of tuples.",
                },
                {
                    "role": "user",
                    "content": f"Extract the car models and years from the following description: {description}. Return the information as a list of tuples: [(car_model, car_year)] if there is a list of years, return one tuple for each year. I only want you to return the list of tuples, nothing else.",
                },
            ],
        )
        # Extraemos la respuesta del modelo
        car_info = response.choices[0].message.content
        return car_info
    except Exception as e:
        print(f"Error al procesar la descripción: {e}")
        return None


errors = []


def process_file(file, bronze_dir, silver_dir):
    with open(os.path.join(bronze_dir, file), "r", encoding="utf-8") as f:
        data = json.load(f)
        description = data["description"]
        car_info = extract_car_info(description)

        if car_info is None:
            errors.append(file)
        else:
            car_info = car_info.replace("‘", "'").replace("’", "'")
            car_info = car_info.replace("“", """).replace("”", """)
            car_info = ast.literal_eval(car_info)
            data["car_info"] = car_info

        # Write back the changes to the file in the silver folder
        with open(os.path.join(silver_dir, file), "w", encoding="utf-8") as silver_file:
            json.dump(data, silver_file, indent=4, ensure_ascii=False)


# Bucle para procesar todos los archivos
for file in bronze_files[1154:]:
    process_file(file, bronze_dir, silver_dir)

# Bucle para reintentar los archivos que fallaron debido a un "Request timed out"
while errors:
    print(f"Reintentando procesar los archivos fallidos: {errors}")

    # Reintentar el procesamiento de los archivos con error
    for file in errors[:]:
        try:
            process_file(file, bronze_dir, silver_dir)
            errors.remove(
                file
            )  # Eliminar el archivo de la lista de errores si fue procesado exitosamente
        except Exception as e:
            print(f"Error procesando {file}: {e}")
            time.sleep(5)  # Pausar 5 segundos antes de intentar de nuevo

    # Si los archivos siguen fallando, puedes aumentar el tiempo de espera para no sobrecargar la API
    if errors:
        print(f"Aún hay archivos con errores. Reintentando en 30 segundos...")
        time.sleep(30)

# Finalmente, si todos los archivos se procesaron, la lista de errores estará vacía
print("Todos los archivos procesados correctamente, errores restantes:", errors)
