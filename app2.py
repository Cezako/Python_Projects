import os  # Pour parcourir les dossiers de l'ordi
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/')
def home():
    # J'ai ajouté un lien pour aller directement à la galerie
    return """
    <h1>Bienvenue !</h1>
    <p>Aller voir <a href="/about">À propos</a></p>
    <p>Aller voir <a href="/galerie">Ma Galerie Photos</a></p>
    """

@app.route('/about')
def about():
    return "À propos de moi..."

# --- NOUVEAU : LA PAGE GALERIE ---
@app.route('/galerie', methods=['GET', 'POST'])
def galerie():
    html = """
    <h1>Galerie de photos locale</h1>
    <form method="POST">
        <label>Chemin du dossier (ex: C:/Users/Toi/Images) :</label><br>
        <input type="text" name="dossier_path" style="width: 300px;">
        <input type="submit" value="Afficher les images">
    </form>
    <hr>
    """

    # Si l'utilisateur a envoyé le formulaire (POST)
    if request.method == 'POST':
        dossier = request.form.get('dossier_path')
        
        # On vérifie si le dossier existe
        if os.path.exists(dossier):
            html += f"<h3>Images trouvées dans : {dossier}</h3>"
            html += "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>"
            
            # On parcourt tous les fichiers du dossier
            for fichier in os.listdir(dossier):
                # On ne garde que les images (jpg, png, gif, jpeg)
                if fichier.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    # L'astuce est ici : la source de l'image appelle notre fonction Python 'voir_image'
                    chemin_complet = os.path.join(dossier, fichier)
                    html += f"""
                        <div style="border: 1px solid #ccc; padding: 5px;">
                            <img src="/voir_image?path={chemin_complet}" height="200"><br>
                            <small>{fichier}</small>
                        </div>
                    """
            html += "</div>"
        else:
            html += "<p style='color:red'>Dossier introuvable ! Vérifie le chemin.</p>"

    return html

# --- NOUVEAU : LA ROUTE MAGIQUE ---
# Cette route sert à "lire" le fichier sur le disque et l'envoyer au navigateur
@app.route('/voir_image')
def voir_image():
    image_path = request.args.get('path')
    return send_file(image_path)

if __name__ == '__main__':
    # On garde ta config qui marche
    app.run(debug=True, port=5001, use_reloader=False)