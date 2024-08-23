import os
from PIL import Image
import pillow_heif

# Chemin vers le dossier contenant les images HEIC
input_dir = "/Users/prichard/miniconda3/envs/infosys/cv_project/data/input/calibration"
output_dir = "/Users/prichard/miniconda3/envs/infosys/cv_project/data/output/calibration"

# Liste des fichiers HEIC dans le dossier
files = sorted(f for f in os.listdir(input_dir) if f.lower().endswith('.heic'))

# Ignorer les fichiers manquants
missing_files = {"IMG_2322.heic", "IMG_2322.HEIC", "IMG_3201.heic", "IMG_3201.HEIC", "IMG_2289.heic", "IMG_2289.HEIC"}
files = [f for f in files if f not in missing_files]

# Initialiser le compteur pour le nommage des fichiers JPEG
count = 0.1

# Créer le dossier de sortie s'il n'existe pas
os.makedirs(output_dir, exist_ok=True)

for file in files:
    # Chemin complet du fichier HEIC
    input_path = os.path.join(input_dir, file)
    
    # Charger l'image HEIC
    heif_file = pillow_heif.open_heif(input_path)
    image = Image.frombytes(
        heif_file.mode, 
        heif_file.size, 
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )

    # Chemin complet du fichier JPEG de sortie
    output_filename = f"{count:.1f}.jpeg"
    output_path = os.path.join(output_dir, output_filename)
    
    # Sauvegarder l'image en JPEG
    image.save(output_path, "JPEG")
    
    # Incrementer le compteur
    count += 0.1
