# Utilisez l'image officielle Python comme image de base
FROM python:3.9-slim

# Définissez le répertoire de travail
WORKDIR /app

# Copiez les fichiers de dépendances et installez-les
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste du code source de l'application
COPY . .

# Commande pour lancer l'application FastAPI
CMD ["uvicorn", "api:scrapp.py", "--host", "0.0.0.0", "--port", "8000"]
