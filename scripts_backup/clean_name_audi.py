import os
import json

# Define the directory containing the JSON files
directory = 'Transformed_data/Audi'

# Define the words to be removed from the 'cleaned_name' field
words_to_remove = ["3 Puertas","5 puertas","Sportback", "Cabrio", "Coupé", "spyder", "Roadster", "GT", "Avant", "L"]

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
        if 'cleaned_name' in data:
            data['cleaned_name'] = clean_name(data['cleaned_name'])
        
        # Write the cleaned data back to the JSON file
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

print("Cleaning completed.")