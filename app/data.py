import pandas as pd
import base64
import io
import re

def load_data(file_path):
    # Charger les données du fichier Excel
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier Excel n'a pas été trouvé à l'emplacement : {file_path}")
    
    # Vérifiez les colonnes nécessaires
    required_columns = [
        'Région', 'Département', 'Nom de l\'établissement', 'Capacité', 'Description', 
        'Latitude', 'Longitude', 'Région Latitude', 'Région Longitude', 'Département Latitude', 'Département Longitude', 'Website'
    ]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Colonne manquante dans le fichier Excel : {col}")

    df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

    regions = df[['Région', 'Région Latitude', 'Région Longitude']].drop_duplicates()
    departments = df[['Département', 'Département Latitude', 'Département Longitude', 'Région']].drop_duplicates()

    # Nettoyage des données de capacité
    df['Capacité'] = df['Capacité'].apply(clean_capacity)

    return df, regions, departments

def load_new_data(contents, filename):
    """
    Charger les nouvelles données depuis un fichier.
    """
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return pd.read_excel(io.BytesIO(decoded))

def save_data(df, filepath):
    """
    Sauvegarder les données dans un fichier.
    """
    df.to_excel(filepath, index=False)

def update_data(df, new_data):
    """
    Mettre à jour les données existantes avec de nouvelles données.
    """
    updated_df = df.copy()
    changes = []
    for index, new_row in new_data.iterrows():
        existing_row = updated_df.loc[updated_df['Nom de l\'établissement'] == new_row['Nom de l\'établissement']]
        if not existing_row.empty:
            for col in new_row.index:
                if existing_row.iloc[0][col] != new_row[col]:
                    updated_df.loc[updated_df['Nom de l\'établissement'] == new_row['Nom de l\'établissement'], col] = new_row[col]
                    changes.append(f"Updated {col} for {new_row['Nom de l\'établissement']}")
        else:
            updated_df = updated_df.append(new_row, ignore_index=True)
            changes.append(f"Added new row for {new_row['Nom de l\'établissement']}")

    return updated_df, changes

def clean_capacity(value):
    match = re.search(r'\d+', str(value))
    return int(match.group()) if match else None
