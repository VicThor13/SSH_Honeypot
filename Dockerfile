# Utilise une image de base Alpine, qui est minimaliste et sécurisée
FROM python:3.11-alpine

# Crée un utilisateur non-root pour exécuter l'application
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Définit le répertoire de travail
WORKDIR /app

# Installe les dépendances nécessaires à la compilation (si besoin pour cryptograpy)
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copie le fichier des exigences
COPY requirements.txt .

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code source de l'application
COPY honeypot.py .

# Change le propriétaire des fichiers pour l'utilisateur non-root
RUN chown -R appuser:appgroup /app

# Bascule sur l'utilisateur non-root
USER appuser

# Expose le port 2222 sur lequel le honeypot écoute
EXPOSE 2222

# Commande par défaut pour exécuter le honeypot
CMD ["python", "honeypot.py"]
