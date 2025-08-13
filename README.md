
# Script de copie de fichiers vers R2 Cloudflare

A brief description of what this project does and who it's for
### Crée l'environnement d'exécution
```
python3 -m venv venv && pip install -r requirements.txt
```
### Créer le fichier .env
```
nano .env
```
```
R2_ACCOUNT_ID=xxxx
R2_ACCESS_KEY_ID=xxxx
R2_SECRET_ACCESS_KEY=xxx
```
### Exécution
```
python multi-upload2.py ./static/ django static
```

