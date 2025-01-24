import os
import json
import pandas as pd

# Function to list all models (JSON file names) for a given brand
def list_models(brand_folder):
    try:
        return [os.path.splitext(file)[0] for file in os.listdir(brand_folder) if file.endswith(".json")]
    except FileNotFoundError:
        return []

# Function to load a model's JSON file
def load_model_json(folder, model):
    file_path = os.path.join(folder, f"{model}.json")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error loading model: {model}.")
        return None

# Function to display a table comparing features
def compare_versions(version1, version2):
    keys = set(version1.keys()).union(version2.keys())
    rows = []
    for key in keys:
        rows.append({
            "Feature": key,
            "Car 1": version1.get(key, "N/A"),
            "Car 2": version2.get(key, "N/A"),
            "Status": "Same" if version1.get(key) == version2.get(key) else "Different"
        })
    table = pd.DataFrame(rows)
    table.to_csv("comparative_cars.csv")
    print("\nComparison Table:")
    print(table.to_string(index=False))

# Main function
def main():
    # Root folder containing subfolders for car brands
    root_folder = "/Users/pablosotogarcia/Desktop/Mioti/Proyecto/scrapper_wallapop/Transformed_data"  # Replace with your actual folder path
    
    # Get list of available brands
    brands = [brand for brand in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, brand))]
    print("Available brands:", ", ".join(brands))
    
    # Prompt user for brand choices
    brand1 = input("¿De qué marca quieres el primer coche? ").strip()
    while brand1 not in brands:
        print("Marca no válida. Por favor, elige entre:", ", ".join(brands))
        brand1 = input("¿De qué marca quieres el primer coche? ").strip()
    
    brand2 = input("¿De qué marca quieres el segundo coche? ").strip()
    while brand2 not in brands:
        print("Marca no válida o ya elegida. Por favor, elige entre:", ", ".join([b for b in brands if b != brand1]))
        brand2 = input("¿De qué marca quieres el segundo coche? ").strip()
    
    # Select models for both brands
    brand1_folder = os.path.join(root_folder, brand1)
    brand1_models = list_models(brand1_folder)
    print(f"Available models for {brand1}: {', '.join(brand1_models)}")
    model1 = input(f"Choose a model from {brand1}: ").strip()
    while model1 not in brand1_models:
        print("Modelo no válido. Por favor, elige entre:", ", ".join(brand1_models))
        model1 = input(f"Choose a model from {brand1}: ").strip()
    
    brand2_folder = os.path.join(root_folder, brand2)
    brand2_models = list_models(brand2_folder)
    print(f"Available models for {brand2}: {', '.join(brand2_models)}")
    model2 = input(f"Choose a model from {brand2}: ").strip()
    while model2 not in brand2_models:
        print("Modelo no válido. Por favor, elige entre:", ", ".join(brand2_models))
        model2 = input(f"Choose a model from {brand2}: ").strip()
    
    # Load JSON data for selected models
    model1_data = load_model_json(brand1_folder, model1)
    model2_data = load_model_json(brand2_folder, model2)
    
    if not model1_data or not model2_data:
        print("Error loading data for selected models.")
        return
    
    # Select versions (motors) for both models
    print(f"Available versions for {brand1}, {model1}:")
    for i, version in enumerate(model1_data["versions"], start=1):
        print(f"{i}. {version['name']}")
    version1_choice = int(input("¿Qué motor quieres para tu primer coche? (Selecciona el número): "))
    version1 = model1_data["versions"][version1_choice - 1]
    
    print(f"Available versions for {brand2}, {model2}:")
    for i, version in enumerate(model2_data["versions"], start=1):
        print(f"{i}. {version['name']}")
    version2_choice = int(input("¿Qué motor quieres para tu segundo coche? (Selecciona el número): "))
    version2 = model2_data["versions"][version2_choice - 1]
    
    # Compare selected versions
    compare_versions(version1, version2)
    

if __name__ == "__main__":
    main()
