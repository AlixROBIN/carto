# scripts/update_data.py

import pandas as pd
import base64
import io

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
