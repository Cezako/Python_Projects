from flask import Flask
import folium  # NOUVEAU : On importe la bibliothèque de cartes

app = Flask(__name__)

@app.route('/')
def home():
    return "Bienvenue sur ma page d'accueil !"

@app.route('/about')
def about():
    return "À propos de moi : Je suis en train d'apprendre à développer des applications web avec Flask !"

@app.route('/carte')
def show_map():

    ma_carte = folium.Map(location=[48.8584, 2.2945], zoom_start=15)

    folium.Marker(
        location=[48.8584, 2.2945],
        popup="Je suis ici !",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(ma_carte)

    return ma_carte._repr_html_()

if __name__ == '__main__':
    app.run(debug=True, port=5001, use_reloader=False)