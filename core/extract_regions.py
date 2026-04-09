import os
import cv2
import json

def extraire_regions():
    base_dir = os.path.dirname(os.path.dirname(__file__)) # Remonte à la racine du projet
    images_dir = os.path.join(base_dir, 'static', 'images')
    labels_dir = os.path.join(base_dir, 'static', 'labels')
    dataset_dir = os.path.join(base_dir, 'dataset_anomalies') # Nouveau dossier pour l'IA
    
    os.makedirs(dataset_dir, exist_ok=True)

    # On parcourt tous les fichiers JSON d'étiquetage
    for label_file in os.listdir(labels_dir):
        if not label_file.endswith('_labels.json'):
            continue
            
        json_path = os.path.join(labels_dir, label_file)
        
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        nom_image = data['image']
        image_path = os.path.join(images_dir, nom_image)
        
        if not os.path.exists(image_path):
            continue
            
        # Chargement de l'image
        img = cv2.imread(image_path)
        
        # Pour chaque boîte dessinée dans l'image
        for index, box in enumerate(data['boxes']):
            x, y = int(box['x']), int(box['y'])
            w, h = int(box['width']), int(box['height'])
            
            # 1. Le "Crop" : On découpe la région
            crop_img = img[y:y+h, x:x+w]
            
            # Vérification de sécurité (si la boîte sort de l'image)
            if crop_img.size == 0:
                continue
                
            # 2. Redimensionnement standard (OBLIGATOIRE pour un CNN/SVM)
            # On force toutes les petites images à faire par exemple 64x64 pixels
            crop_resized = cv2.resize(crop_img, (64, 64))
            
            # 3. Sauvegarde de la vignette
            # Pour l'instant, ton outil JS sauvegarde le label "anomalie"
            label = box.get('label', 'anomalie') 
            dossier_classe = os.path.join(dataset_dir, label)
            os.makedirs(dossier_classe, exist_ok=True)
            
            nom_vignette = f"{nom_image.split('.')[0]}_crop_{index}.jpg"
            cv2.imwrite(os.path.join(dossier_classe, nom_vignette), crop_resized)
            
    print(f"✅ Extraction terminée ! Les vignettes sont dans {dataset_dir}")

if __name__ == "__main__":
    extraire_regions()