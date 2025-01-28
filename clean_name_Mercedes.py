import os
import json

# Define the directory containing the JSON files
directory = 'Transformed_data/Mercedes-Benz'

# Define the words to be removed from the 'cleaned_name' field
words_to_remove = ["",""]
# Function to clean the 'cleaned_name' field
def clean_name(name, ):
    for word in words_to_remove:
        # Caso especial dentro del bucle
        if name == "AMG GT 4 puertas Coupé": name = "AMG GT 4-Door Coupé"
        if name 
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
            data['name'] = clean_name(data['name'], data[''])
        
        # Write the cleaned data back to the JSON file
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

print("Cleaning completed.")