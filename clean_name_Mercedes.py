import os
import json

# Define the directory containing the JSON files
directory = 'Transformed_data/Mercedes-Benz'

# Define the words to be removed from the 'cleaned_name' field
words_to_remove = ["Coupé","Roadster", "Extralarga", "Cabrio", "Berlina", "All-Terrain","Largo", "Stirling Moss", "Compacta", "Larga", "Extralarga", "Compacta", "Extralargo", "Compacto", "Corto"]
# Function to clean the 'cleaned_name' field
def clean_name(name):
    if name.startswith("AMG"): return name
    if name.startswith("Citan"): name = "Citan"
    if name.startswith("CL"): name = "CL Coupe"
    if name.startswith("Clase C"): name = "Clase C"
    if name.startswith("Clase E"): name = "Clase E"
    if name.startswith("Clase S"): name = "Clase S"
    if name.startswith("Clase V"): name = "Clase V"
    if name.startswith("Clase X"): name = "Clase X"
    if name.startswith("Clase G"): name = "Clase G"
    if name.startswith("Clase A"): name = "Clase A"
    if name.startswith("Clase B"): name = "Clase B"
    if name.startswith("Clase GLA"): name = "GLA"
    if name.startswith("Clase GLB"): name = "GLB"
    if name.startswith("Clase GLC"): name = "GLC"
    if name.startswith("Clase GLE"): name = "GLE"
    if name.startswith("Clase GLS"): name = "GLS"
    if name.startswith("Clase SLC"): name = "GLC"
    if name.startswith("Clase SL"): name = "SL"
    if name.startswith("Clase SLK"): name = "SLK"
    if name.startswith("Clase SLR"): name = "SLR"
    if name.startswith("Clase SLK"): name = "SLK"
    if name.startswith("SLS"): name = "SLS"
    if name.startswith("EQA"): name = "EQA (H243)"
    if name.startswith("EQB"): name = "EQB (X243)"
    if name.startswith("EQC"): name = "EQC (N293)"
    if name.startswith("EQE"): name = "EQE (V297)"
    if name.startswith("EQE SUV"): name = "EQE SUV (Z294)"
    if name.startswith("EQS"): name = "EQS (V297)"

    for word in words_to_remove:
        # Caso especial dentro del bucle
        if name == "AMG GT 4 puertas Coupé": name = "AMG GT 4-Door Coupé"
        # Reemplazar las palabras no deseadas
        name = name.replace(word, "")

    return name.strip()
# Iterate over all JSON files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        
        # Read the JSON file
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Clean the 'cleaned_name' field
        if 'name' in data:
            data['name'] = clean_name(data['name'])
        
        # Write the cleaned data back to the JSON file
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

print("Cleaning completed.")