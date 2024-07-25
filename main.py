import os
import pandas as pd
from dash import Dash
import dash_bootstrap_components as dbc

from app.layout import create_layout
from app.callbacks import register_callbacks
from app.data import load_data

# Construction du chemin complet vers le fichier Excel
chemin_fichier = r"C:\Users\arobin\Documents\projet2\data\compiled_data_bon.xlsx"
chemin_nouveau_fichier = r"C:\Users\arobin\Documents\projet2\data\new_data.xlsx"

# Vérification de l'existence du fichier
if not os.path.exists(chemin_fichier):
    raise FileNotFoundError(f"Le fichier Excel n'a pas été trouvé à l'emplacement : {chemin_fichier}")

# Chargement des données depuis le fichier Excel
df, regions, departments = load_data(chemin_fichier)

# Initialisation de l'application Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Définition du layout de l'application
app.layout = create_layout(app, regions)
app.config.suppress_callback_exceptions = True

# Enregistrement des callbacks
register_callbacks(app, df, regions, departments, chemin_fichier, chemin_nouveau_fichier)

# Exécution de l'application
if __name__ == '__main__':
    app.run_server(debug=True)
