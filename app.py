import os
import cv2
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from core.segmentation import segment_image_kmeans

import markdown

app = Flask(__name__)

# --- CONFIGURATION DES DOSSIERS ---
BASE_DIR = app.root_path
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
RESULTS_FOLDER = os.path.join(BASE_DIR, 'static', 'results')
LABELS_FOLDER = os.path.join(BASE_DIR, 'static', 'labels')

# verification if exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(LABELS_FOLDER, exist_ok=True)

# Extensions autorisées pour l'upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- 1. ROUTE D'ACCUEIL (DASHBOARD) ---

@app.route('/')
def home():
    # filtre dossier img
    images = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    return render_template('index.html', images=images)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Gère l'ajout d'une nouvelle image depuis l'interface web"""
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename) # Sécurité contre le piratage
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return redirect(url_for('home')) # Recharge l'accueil
        
    return "Fichier non autorisé", 400


# --- 2. ROUTES DE SEGMENTATION ---

@app.route('/segment/<filename>')
def segment(filename):
    base_dir = app.root_path
    input_path = os.path.join(base_dir, 'static', 'images', filename)
    output_filename = f"seg_{filename}"
    output_path = os.path.join(base_dir, 'static', 'results', output_filename)
    
    if not os.path.exists(input_path):
        return "Erreur 404", 404

    # Traitement IA
    result_img, labels = segment_image_kmeans(input_path, k=4)
    cv2.imwrite(output_path, cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR))
    
    # --- Lecture et conversion du Markdown ---
    doc_path = os.path.join(base_dir, 'static', 'docs', 'explications.md')
    documentation_html = "<p>Fichier de documentation introuvable.</p>"
    
    if os.path.exists(doc_path):
        with open(doc_path, 'r', encoding='utf-8') as f:
            texte_md = f.read()
            # Convertit le texte markdown en balises HTML
            documentation_html = markdown.markdown(texte_md) 
    
    # variable `documentation` au render_template
    return render_template('visualisation.html', 
                           image_originale=filename, 
                           image_segmentee=output_filename,
                           documentation=documentation_html)


# --- 3. ROUTES D'ÉTIQUETAGE ---

@app.route('/label/<filename>')
def label_image(filename):
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(input_path):
        return "Image introuvable", 404
    return render_template('labeling.html', image_name=filename)

@app.route('/api/save_labels/<filename>', methods=['POST'])
def save_labels(filename):
    data = request.json
    json_filename = filename.split('.')[0] + '_labels.json'
    json_path = os.path.join(LABELS_FOLDER, json_filename)
    
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)
        
    return jsonify({"status": "success", "message": "Sauvegardé avec succès !"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)