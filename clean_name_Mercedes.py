import os
import json

# Define the directory containing the JSON files
directory = 'Transformed_data/Mercedes-Benz'

# Define the words to be removed from the 'cleaned_name' field
words_to_remove = ["Coupé", "Roadster", "Shooting Brake", "Sedán", "Berlina", "Familiar", "SportCoupé", "Estate", "Cabrio", "All-Terrain", "Familiar", "Largo", "Larga", "Extralargo", "Compacta", "Stirling Mose", "Doble Cabina", "Compacto", "Maybach", "Batalla Corta", "Batalla Larga", "Corto", "4x4²", "SUV"]

# Function to clean the 'cleaned_name' field
def clean_name(name):
    for word in words_to_remove:
        name = name.replace(word, "")
    return name.strip()

# Iterate over all JSON files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        
        # Read the JSON file
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        # Mercedes benz C192 filter
        if data.get('name') == 'AMG GT' and int(data.get('year')) >= 2024:
            data['name'] = 'AMG GT (192)'
        elif data.get('name') == 'AMG GT' and int(data.get('year')) <= 2024:
            data['name'] = 'AMG GT (190)'
        # Clean the 'cleaned_name' field
        if 'name' in data:
            data['name'] = clean_name(data['name'])
        
        # Write the cleaned data back to the JSON file
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

print("Cleaning completed.")