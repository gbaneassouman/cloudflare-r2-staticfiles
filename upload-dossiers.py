import os
import sys
from pathlib import Path
import boto3
from dotenv import load_dotenv

# Charger .env
load_dotenv()

if len(sys.argv) != 3:
    print("Usage: python upload.py <path> <bucket>")
    sys.exit(1)

path = Path(sys.argv[1])
bucket_name = sys.argv[2]

# Charger les variables R2
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
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    region_name="auto",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
)

def upload_file(file_path: Path, bucket: str, key: str):
    """Upload un fichier unique."""
    try:
        s3.upload_file(str(file_path), bucket, key)
        print(f"✅ Uploaded: {key}")
    except Exception as e:
        print(f"❌ Erreur upload {key} : {e}")

def upload_directory(dir_path: Path, bucket: str):
    """Upload récursif d'un dossier (y compris sous-dossiers)."""
    has_files = False
    for root, _, files in os.walk(dir_path):
        for filename in files:
            full_path = Path(root) / filename
            key = str(full_path.relative_to(dir_path))
            upload_file(full_path, bucket, key)
            has_files = True
    # Si le dossier est vide, créer une clé dossier/
    if not has_files:
        folder_key = f"{dir_path.name}/"
        try:
            s3.put_object(Bucket=bucket, Key=folder_key)
            print(f"📂 Dossier vide créé: {folder_key}")
        except Exception as e:
            print(f"❌ Erreur création dossier vide {folder_key} : {e}")

# Détection fichier ou dossier
if path.is_file():
    upload_file(path, bucket_name, path.name)
elif path.is_dir():
    upload_directory(path, bucket_name)
else:
    print("Erreur : Le chemin fourni n'existe pas ou n'est pas valide.")
    sys.exit(1)
