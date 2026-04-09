# Documentation des Verrous et Corrections

Lors de la segmentation des images marines, plusieurs défis (verrous) ont été rencontrés et traités :

## 1. Le Volume des données
Les images d'origine (comme les MFDC) sont de haute résolution, ce qui consomme beaucoup de RAM.
* **Correction apportée :** Redimensionnement (Resize) des images avant le traitement pour accélérer l'algorithme K-Means sans perdre la sémantique de l'image.

## 2. La Luminosité et les Reflets
La surface de l'eau crée des reflets spéculaires intenses qui faussent le clustering des couleurs (le K-Means confond le reflet blanc avec un bateau blanc).
* **Correction apportée :** Utilisation de l'algorithme **CLAHE** sur le canal de luminosité pour égaliser les contrastes locaux.

## 3. Le Bruit de Segmentation
L'algorithme K-Means produit souvent des pixels isolés (bruit "poivre et sel").
* **Correction apportée :** Application d'une **Ouverture Morphologique** (Érosion suivie d'une Dilatation) via OpenCV pour lisser les formes et supprimer les petits artefacts.