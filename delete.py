import os
import sys
import boto3
from dotenv import load_dotenv

# Charger .env
load_dotenv()

if len(sys.argv) != 3:
    print("Usage: python delete_folder.py <bucket> <folder_path>")
    sys.exit(1)

bucket_name = sys.argv[1]
folder_path = sys.argv[2].rstrip("/") + "/"  # Forcer le slash à la fin

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

# Lister tous les objets dans le dossier
objects_to_delete = []
paginator = s3.get_paginator("list_objects_v2")

print(f"📂 Recherche des objets à supprimer dans: {folder_path}")

for page in paginator.paginate(Bucket=bucket_name, Prefix=folder_path):
    for obj in page.get("Contents", []):
        objects_to_delete.append({"Key": obj["Key"]})

if not objects_to_delete:
    print("⚠️ Aucun fichier trouvé à supprimer.")
    sys.exit(0)

# Supprimer par batch de 1000 (limite S3 API)
print(f"🚀 Suppression de {len(objects_to_delete)} objets...")
for i in range(0, len(objects_to_delete), 1000):
    batch = objects_to_delete[i:i + 1000]
    s3.delete_objects(Bucket=bucket_name, Delete={"Objects": batch})

print(f"✅ Dossier '{folder_path}' et tout son contenu ont été supprimés.")
