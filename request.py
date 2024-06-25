import json
import requests
import os

# Obtenir le répertoire courant du script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construire le chemin relatif vers le fichier utilisateur.json
json_file_path = os.path.join(current_dir, 'utilisateur.json')

# Lire le contenu du fichier JSON
with open(json_file_path, 'r') as file:
    data = json.load(file)

# URL de l'API Flask
url = "http://localhost:5000/scrape"

# Envoyer la requête POST
response = requests.post(url, json=data)

# Afficher la réponse
print(response.json())
