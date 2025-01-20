import os
import json

# Define the directory containing the JSON files
directory = 'Transformed_data/BMW'

# Define the words to be removed from the 'cleaned_name' field
words_to_remove = ["3p", "5p", "Berlina", "Gran Coupé", "Touring", "Cabrio", "Coupé", "Compact","5 puertas","3 puertas","4 puertas","Batalla normal", "Gran Turismo", "Batalla larga", "Active Tourer","Gran Tourer","Batalla", "Roadster"]

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
        
        # Clean the 'cleaned_name' field
        if 'name' in data:
            data['name'] = clean_name(data['name'])
        
        # Write the cleaned data back to the JSON file
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

print("Cleaning completed.")