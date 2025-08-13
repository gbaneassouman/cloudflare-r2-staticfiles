import os
import sys
from pathlib import Path
import boto3
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Charger .env
load_dotenv()

if len(sys.argv) != 4:
    print("Usage: python upload.py <path> <bucket> <remote_folder>")
    sys.exit(1)

path = Path(sys.argv[1])
bucket_name = sys.argv[2]
remote_folder = sys.argv[3].rstrip("/")  # Supprimer slash final si présent

# Charger les variables R2
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")

if not R2_ACCOUNT_ID or not R2_ACCESS_KEY_ID or not R2_SECRET_ACCESS_KEY:
    print("Erreur : Variables manquantes dans le fichier .env")
    sys.exit(1)

# Configurer boto3
session = boto3.session.Session()
s3 = session.client(
    "s3",
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    region_name="auto",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
)

def upload_file(file_path: Path, key: str):
    """Upload un fichier unique."""
    try:
        s3.upload_file(str(file_path), bucket_name, key)
        return True
    except Exception as e:
        print(f"\n❌ Erreur upload {key} : {e}")
        return False

def upload_directory(dir_path: Path):
    """Upload récursif d'un dossier vers un dossier du bucket."""
    all_files = []
    for root, _, files in os.walk(dir_path):
        for filename in files:
            full_path = Path(root) / filename
            relative_path = str(full_path.relative_to(dir_path))
            key = f"{remote_folder}/{relative_path}"
            all_files.append((full_path, key))

    if not all_files:
        # Dossier vide → créer un objet "remote_folder/"
        folder_key = f"{remote_folder}/{dir_path.name}/"
        try:
            s3.put_object(Bucket=bucket_name, Key=folder_key)
            print(f"📂 Dossier vide créé: {folder_key}")
        except Exception as e:
            print(f"❌ Erreur création dossier vide {folder_key} : {e}")
        return

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(upload_file, f, k) for f, k in all_files]
        with tqdm(total=len(all_files), desc="📤 Upload en cours", unit="fichier") as pbar:
            for future in as_completed(futures):
                future.result()
                pbar.update(1)

# Détection fichier ou dossier
if path.is_file():
    key = f"{remote_folder}/{path.name}"
    with tqdm(total=1, desc="Upload en cours", unit="fichier") as pbar:
        upload_file(path, key)
        pbar.update(1)
elif path.is_dir():
    upload_directory(path)
else:
    print("Erreur : Le chemin fourni n'existe pas ou n'est pas valide.")
    sys.exit(1)
