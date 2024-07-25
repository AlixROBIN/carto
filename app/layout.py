from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_leaflet as dl

def create_layout(app, regions):
    layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Cartographie des Acteurs de la protection de l'enfance", className='text-center'),
                dcc.Dropdown(
                    id='region-dropdown',
                    options=[{'label': region, 'value': region} for region in regions['Région']],
                    placeholder='Sélectionnez une région',
                    multi=True,  # Permettre la multi-sélection
                    searchable=True  # Ajouter une barre de recherche
                ),
                dcc.Dropdown(
                    id='departement-dropdown',
                    placeholder='Sélectionnez un département',
                    multi=True,  # Permettre la multi-sélection
                    searchable=True  # Ajouter une barre de recherche
                ),
                dcc.Dropdown(
                    id='type-dropdown',
                    placeholder='Sélectionnez un type d\'établissement',
                    multi=True,  # Permettre la multi-sélection
                    searchable=True  # Ajouter une barre de recherche
                ),
                dcc.Dropdown(
                    id='etablissement-dropdown',
                    placeholder='Sélectionnez un établissement',
                    multi=True,  # Permettre la multi-sélection
                    searchable=True  # Ajouter une barre de recherche
                ),
                dbc.Button("Activer la recherche sur site", id='search-button', color='primary', className='mr-1'),
                dbc.Button("Mettre à jour les données", id='update-button', color='success', className='mr-1'),
                dbc.Button("Réinitialiser", id='reset-button', color='danger', className='mr-1')
            ], width=4),
            dbc.Col([
                dl.Map(
                    id='map',
                    center=[46.603354, 1.888334],
                    zoom=6,
                    style={'width': '100%', 'height': '500px'},
                    children=[
                        dl.TileLayer(),
                    ]
                ),
                html.Div(id='recap')
            ], width=8)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id='update-output', className='mt-3'),
                html.Div(id='scrape-output', className='mt-3')
            ])
        ]),
        dbc.Toast(
            id='toast-container',
            is_open=False,
            dismissable=True,
            duration=4000,
            children=''
        )
    ], fluid=True)
    return layout
