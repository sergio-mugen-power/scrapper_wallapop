import json
import os
import matplotlib.pyplot as plt


dir="/Users/pablosotogarcia/Desktop/Mioti/Proyecto/scrapper_wallapop/Transformed_data/Audi"
os.chdir(dir)

file="/Users/pablosotogarcia/Desktop/Mioti/Proyecto/scrapper_wallapop/Transformed_data/Audi/A6_Avant_2012.json"

with open(file, 'r') as f:
    data = json.load(f)

# Print the data
print(type(data))
print(type(data["versions"]))
print((data["versions"][0].keys())) #features from each engine model 
print(type(data["versions"][0]))
print((data["versions"][0]["potencia"]))

engines=data["versions"]
models=[]
power=[]
for i in range(len(engines)):
    models.append(engines[i]["name"])
    power.append(engines[i]["potencia"])
    print(engines[i]["potencia"], " " ,engines[i]["name"])
print(i)

# Crear el gráfico
plt.figure(figsize=(12, 6))
plt.barh(models, power, color='skyblue', edgecolor='black')

# Configurar el gráfico
plt.xlabel('Potencia (kW)')
plt.ylabel('Modelo')
plt.title('Potencia (kW) por Modelo')
plt.tight_layout()

# Mostrar el gráfico
plt.show()