import os
import json

current_path = os.getcwd()
landing_path = os.path.join(current_path, "datasets", "motorlist", "1_landing")
bronze_path = os.path.join(current_path, "datasets", "motorlist", "2_bronze")


def normalize_fuel_consumption(doc):
    # Buscar claves que contengan "Fuel consumption, L/100 km"
    for key in list(doc.keys()):
        if key.startswith("Fuel consumption, L/100 km"):
            try:  # Caso en el que existen 3 valores
                # Dividir los valores y crear los nuevos campos
                values = doc[key].split(".")  # Separar por el punto decimal
                if len(values) >= 3:  # Asegurarse de que haya 3 valores
                    doc["city_fuel_consumption"] = float(values[0] + "." + values[1][0])
                    doc["highway_fuel_consumption"] = float(
                        values[1][1:] + "." + values[2][0]
                    )
                    doc["combined_fuel_consumption"] = float(
                        values[2][1:] + "." + values[3]
                    )

            except:  # Caso en el que existen 2 valores
                values = doc[key].split("-")  # Separar por el punto decimal
                if len(values) == 2:  # Asegurarse de que haya 3 valores
                    doc["city_fuel_consumption"] = float(values[0])
                    doc["highway_fuel_consumption"] = float(values[1])
                # Eliminar el campo original
            del doc[key]
    return doc


def clean_and_convert(data):
    cleaned_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Quitar el símbolo "~"
            clean_value = value.replace("~", "").strip()
            try:
                # Intentar convertir el valor limpio a float (eliminar espacios en números grandes)
                numeric_value = float(clean_value.replace(" ", ""))
                cleaned_data[key] = numeric_value
            except ValueError:
                # Si no es convertible, guardar como texto limpio
                cleaned_data[key] = clean_value
        else:
            # Si no es cadena, mantener el valor original
            cleaned_data[key] = value
    return cleaned_data


# Recorrer todos los archivos JSON en la carpeta
for filename in os.listdir(landing_path):
    if filename.endswith(".json"):
        file_path = os.path.join(landing_path, filename)
        print(f"Importando {file_path}...")

        # Cargar el archivo JSON y guardarlo en MongoDB
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)  # Leer el contenido del archivo JSON
            if isinstance(data, list):  # Si el archivo tiene una lista de objetos
                data = [normalize_fuel_consumption(doc) for doc in data]
                data = clean_and_convert(data)
                bronze_file_name = os.path.join(bronze_path, filename)
                # Guarda el diccionario en un archivo JSON
                with open(bronze_file_name, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

            else:  # Si el archivo tiene un solo objeto
                data = normalize_fuel_consumption(data)
                data = clean_and_convert(data)
                bronze_file_name = os.path.join(bronze_path, filename)
                # Guarda el diccionario en un archivo JSON
                with open(bronze_file_name, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)


print("Transformacion Completa.")
