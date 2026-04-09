import os
import cv2
import numpy as np
from skimage.feature import hog
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

def train_classifier():
    # 1. Définition des chemins
    base_dir = os.path.dirname(os.path.dirname(__file__))
    dataset_dir = os.path.join(base_dir, 'dataset_anomalies')
    model_path = os.path.join(base_dir, 'core', 'svm_model.pkl')

    print("⏳ Chargement des images et extraction des caractéristiques HOG...")
    
    features = []
    labels = []
    
    # 2. Parcours du dataset
    classes = os.listdir(dataset_dir)
    
    for nom_classe in classes:
        chemin_classe = os.path.join(dataset_dir, nom_classe)
        if not os.path.isdir(chemin_classe):
            continue
            
        for nom_image in os.listdir(chemin_classe):
            img_path = os.path.join(chemin_classe, nom_image)
            img = cv2.imread(img_path)
            
            if img is None:
                continue
                
            # Les images doivent être à la même taille (le script de crop faisait du 64x64)
            img = cv2.resize(img, (64, 64))
            
            # HOG fonctionne mieux en niveaux de gris (on cherche les formes, pas la couleur)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 3. Extraction des features HOG
            # (Ces paramètres sont classiques pour des images 64x64)
            hog_features = hog(gray, orientations=9, pixels_per_cell=(8, 8),
                               cells_per_block=(2, 2), block_norm='L2-Hys', 
                               visualize=False)
            
            features.append(hog_features)
            labels.append(nom_classe)

    if len(features) == 0:
        print("❌ Erreur : Aucune image trouvée dans dataset_anomalies/.")
        return

    # Conversion en tableaux NumPy
    X = np.array(features)
    y = np.array(labels)

    # 4. Séparation : 80% pour l'entraînement, 20% pour le test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print(f"📊 Données prêtes : {len(X_train)} pour l'entraînement, {len(X_test)} pour le test.")
    print("🧠 Entraînement du modèle SVM en cours...")

    # 5. Création et entraînement du SVM
    # Le kernel 'linear' est souvent le plus performant avec HOG
    svm_model = SVC(kernel='linear', probability=True, random_state=42)
    svm_model.fit(X_train, y_train)

    # 6. Évaluation des performances
    y_pred = svm_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✅ Entraînement terminé !")
    print(f"🎯 Précision (Accuracy) sur les données de test : {accuracy * 100:.2f}%\n")
    
    # Affiche un rapport détaillé (professeurs adorent ça)
    print("--- Rapport de Classification ---")
    print(classification_report(y_test, y_pred))

    # 7. Sauvegarde du modèle
    joblib.dump(svm_model, model_path)
    print(f"💾 Modèle sauvegardé avec succès sous : {model_path}")

if __name__ == "__main__":
    train_classifier()