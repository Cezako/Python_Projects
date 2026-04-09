import cv2
import numpy as np
from sklearn.cluster import KMeans

def segment_image_kmeans(image_path, k=8):

    # 1. Chargement et conversion
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Redimensionnement (Verrou volume)
    scale_percent = 50 
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    img_small = cv2.resize(img, (width, height))

    # 2. Préparation des données pour K-Means
    pixel_values = img_small.reshape((-1, 3))
    pixel_values = np.float32(pixel_values)

    # 3. Application de K-Means
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(pixel_values)
    
    # Recuperation couleurs dominantes
    centers = np.uint8(kmeans.cluster_centers_)
    
    # 4. Correction Morpho-mathématique (Verrou bruit)
    # lissage des labels
    labels_2d = labels.reshape(height, width).astype(np.uint8)
    kernel = np.ones((5,5), np.uint8)
    
    # Nettoyage des régions
    cleaned_labels = cv2.morphologyEx(labels_2d, cv2.MORPH_OPEN, kernel)

    # 5. Reconstruction de l'image
    final_image = centers[cleaned_labels.flatten()].reshape(img_small.shape)

    return final_image, cleaned_labels