import os
import io
import base64
import cv2
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from flask import Flask, request, send_file, redirect, url_for

app = Flask(__name__)

def get_image_dataframe(image_path, size_limit=None):
    img = cv2.imread(image_path)
    if img is None: return None, None, None
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    original_shape = img_rgb.shape

    if size_limit:
        img_rgb = cv2.resize(img_rgb, size_limit)

    pixels = img_rgb.reshape((-1, 3))
    df = pd.DataFrame(pixels, columns=['R', 'G', 'B'])
    return df, original_shape, img_rgb

def generate_elbow_plot(df):
    sse = []
    df_sample = df.sample(n=min(3000, len(df)), random_state=42)
    
    K_range = range(1, 11)
    for k in K_range:
        kmeans = KMeans(n_clusters=k, n_init=5, max_iter=100, random_state=42)
        kmeans.fit(df_sample)
        sse.append(kmeans.inertia_)

    plt.figure(figsize=(6, 4))
    plt.style.use("ggplot")
    plt.plot(K_range, sse, marker='o')
    plt.xlabel("Nombre de clusters (k)")
    plt.ylabel("Inertie")
    plt.title("Méthode du Coude")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def apply_kmeans_final(image_path, k):
    df, shape, _ = get_image_dataframe(image_path)
    if df is None: return None

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=5)
    kmeans.fit(df)
    
    centers = kmeans.cluster_centers_.astype(int)
    new_colors = centers[kmeans.labels_]
    
    img_reconstructed = new_colors.reshape(shape).astype(np.uint8)
    img_bgr = cv2.cvtColor(img_reconstructed, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode('.jpg', img_bgr)
    return base64.b64encode(buffer).decode('utf-8')

@app.route('/')
def home():
    return redirect(url_for('galerie'))

@app.route('/voir_image')
def voir_image():
    return send_file(request.args.get('path'))

@app.route('/galerie', methods=['GET', 'POST'])
def galerie():
    style = """
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 20px auto; padding: 20px; }
        select { padding: 10px; width: 100%; font-size: 16px; margin: 10px 0; }
        input[type="text"] { padding: 10px; width: 70%; }
        input[type="submit"] { padding: 10px 20px; cursor: pointer; background: #007bff; color: white; border: none; }
        .box { border: 1px solid #ddd; padding: 20px; margin-bottom: 20px; border-radius: 8px; background: #f9f9f9; }
    </style>
    """
    
    html = f"{style}<h1>1. Sélection de l'image</h1>"
    dossier_actuel = request.form.get('dossier_path') or "C:/"
    
    html += f"""
    <div class="box">
        <form method="POST">
            <label><b>Chemin du dossier :</b></label><br>
            <input type="text" name="dossier_path" value="{dossier_actuel}">
            <input type="submit" value="Charger la liste">
        </form>
    </div>
    """

    if request.method == 'POST' and os.path.exists(dossier_actuel):
        fichiers_images = []
        try:
            for f in os.listdir(dossier_actuel):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    fichiers_images.append(f)
        except:
            pass
        
        if fichiers_images:
            html += f"""
            <div class="box" style="border-left: 5px solid green;">
                <h3>{len(fichiers_images)} images trouvées. Choisissez-en une :</h3>
                <form action="/analyse" method="POST">
                    <input type="hidden" name="image_path_hidden" value="{dossier_actuel}">
                    <label>Fichier :</label>
                    <select name="selected_filename" size="10">
            """
            for img_name in fichiers_images:
                full_path = os.path.join(dossier_actuel, img_name)
                html += f'<option value="{full_path}">{img_name}</option>'
            
            html += """
                    </select>
                    <br><br>
                    <input type="submit" value="Lancer l'Analyse (Coude)" style="background: green; width: 100%;">
                </form>
            </div>
            """
        else:
            html += "<p style='color:red'>Aucune image dans ce dossier.</p>"

    return html

@app.route('/analyse', methods=['POST'])
def analyse():
    image_path = request.form.get('selected_filename')
    if not image_path: return "Aucune image sélectionnée."

    df, _, _ = get_image_dataframe(image_path, size_limit=(150, 150))
    plot_base64 = generate_elbow_plot(df)

    return f"""
    <div style="font-family: sans-serif; text-align: center;">
        <h1>2. Analyse par la méthode du Coude</h1>
        <div style="display:flex; justify-content:center; gap:20px; align-items:center;">
            <div>
                <h3>Image choisie</h3>
                <img src="/voir_image?path={image_path}" style="max-height: 400px; max-width: 400px; border: 2px solid #333;">
            </div>
            <div>
                <h3>Graphique d'Inertie</h3>
                <img src="data:image/png;base64,{plot_base64}" style="border: 1px solid #ddd;">
            </div>
        </div>
        
        <div style="background: #eee; padding: 20px; margin-top: 20px;">
            <form action="/resultat" method="POST">
                <input type="hidden" name="path" value="{image_path}">
                <label style="font-size: 1.2em;"><b>Choisissez le K optimal (le coude) : </b></label>
                <input type="number" name="k" min="2" max="20" value="3" style="font-size: 1.2em; width: 60px;">
                <input type="submit" value="Segmenter l'image" style="font-size: 1.2em; background: #28a745; color: white; border: none; padding: 10px;">
            </form>
        </div>
        <br>
        <a href="/galerie">← Retour au choix</a>
    </div>
    """

@app.route('/resultat', methods=['POST'])
def resultat():
    path = request.form.get('path')
    k = int(request.form.get('k'))
    
    img_final_b64 = apply_kmeans_final(path, k)
    
    return f"""
    <div style="font-family: sans-serif; text-align: center;">
        <h1>Résultat de la Segmentation (K={k})</h1>
        <div style="display: flex; justify-content: center; gap: 10px;">
            <img src="/voir_image?path={path}" style="max-height: 80vh; max-width: 45%;">
            <img src="data:image/jpeg;base64,{img_final_b64}" style="max-height: 80vh; max-width: 45%; border: 2px solid red;">
        </div>
        <br>
        <form action="/analyse" method="POST">
            <input type="hidden" name="selected_filename" value="{path}">
            <input type="submit" value="Changer K (Retour analyse)">
        </form>
        <a href="/galerie">Choisir une autre image</a>
    </div>
    """

if __name__ == '__main__':
    app.run(debug=True, port=5001)