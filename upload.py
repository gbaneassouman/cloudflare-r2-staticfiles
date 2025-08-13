import os
import sys
from pathlib import Path
import boto3
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

if len(sys.argv) != 3:
    print("Usage: python upload.py <directory> <bucket>")
    sys.exit(1)

directory = Path(sys.argv[1])
bucket_name = sys.argv[2]

# Vérification du dossier
if not directory.exists() or not directory.is_dir():
    print(f"Erreur : {directory} n'est pas un dossier valide.")
    sys.exit(1)

# Charger les variables du .env
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")

if not R2_ACCOUNT_ID or not R2_ACCESS_KEY_ID or not R2_SECRET_ACCESS_KEY:
    print("Erreur : Variables manquantes dans le fichier .env")
    sys.exit(1)

# Configurer le client boto3
session = boto3.session.Session()
s3 = session.client(
    "s3",
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com/django",
    region_name="auto",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
)

# Upload récursif
for root, _, files in os.walk(directory):
    for filename in files:
        full_path = Path(root) / filename
        key = str(full_path.relative_to(directory))
        try:
            s3.upload_file(str(full_path), bucket_name, key)
            print(f"Uploaded: {key}")
        except Exception as e:
            print(f"Erreur upload {key} : {e}")
