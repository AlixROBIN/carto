import os
import pandas as pd
from dash import Input, Output, State, callback_context, no_update, dcc, html
import dash_leaflet as dl
import dash_bootstrap_components as dbc
from app.data import load_data, save_data, update_data, load_new_data, clean_capacity
import asyncio
from scripts.scrape_data import scrape_data_async

def register_callbacks(app, df, regions, departments, chemin_fichier, chemin_nouveau_fichier):
    print("Aperçu des données du fichier Excel :")
    print(df.head())

    global df_global
    df_global = df.copy()

    @app.callback(
        Output('departement-dropdown', 'options'),
        [Input('region-dropdown', 'value')]
    )
    def update_departement_dropdown(selected_region):
        print(f"update_departement_dropdown called with region: {selected_region}")
        if selected_region is None:
            return []
        if isinstance(selected_region, list):
            filtered_df = departments[departments['Région'].isin(selected_region)]
        else:
            filtered_df = departments[departments['Région'] == selected_region]
        options = [{'label': d, 'value': d} for d in filtered_df['Département'].unique()]
        print(f"Filtered departments: {options}")
        return options

    @app.callback(
        Output('type-dropdown', 'options'),
        [Input('region-dropdown', 'value'),
         Input('departement-dropdown', 'value')]
    )
    def update_type_dropdown(selected_region, selected_departement):
        print(f"update_type_dropdown called with region: {selected_region}, department: {selected_departement}")
        filtered_df = df_global
        if selected_region:
            if isinstance(selected_region, list):
                filtered_df = filtered_df[filtered_df['Région'].isin(selected_region)]
            else:
                filtered_df = filtered_df[filtered_df['Région'] == selected_region]
        if selected_departement:
            if isinstance(selected_departement, list):
                filtered_df = filtered_df[filtered_df['Département'].isin(selected_departement)]
            else:
                filtered_df = filtered_df[filtered_df['Département'] == selected_departement]
        options = [{'label': t, 'value': t} for t in filtered_df['Type d\'établissement'].unique()]
        print(f"Filtered types: {options}")
        return options

    @app.callback(
        Output('etablissement-dropdown', 'options'),
        [Input('region-dropdown', 'value'),
         Input('departement-dropdown', 'value'),
         Input('type-dropdown', 'value')]
    )
    def update_etablissement_dropdown(selected_region, selected_departement, selected_type):
        print(f"update_etablissement_dropdown called with region: {selected_region}, department: {selected_departement}, type: {selected_type}")
        filtered_df = df_global
        if selected_region:
            if isinstance(selected_region, list):
                filtered_df = filtered_df[filtered_df['Région'].isin(selected_region)]
            else:
                filtered_df = filtered_df[filtered_df['Région'] == selected_region]
        if selected_departement:
            if isinstance(selected_departement, list):
                filtered_df = filtered_df[filtered_df['Département'].isin(selected_departement)]
            else:
                filtered_df = filtered_df[filtered_df['Département'] == selected_departement]
        if selected_type:
            if isinstance(selected_type, list):
                filtered_df = filtered_df[filtered_df['Type d\'établissement'].isin(selected_type)]
            else:
                filtered_df = filtered_df[filtered_df['Type d\'établissement'] == selected_type]
        options = [{'label': e, 'value': e} for e in filtered_df['Nom de l\'établissement'].unique()]
        print(f"Filtered establishments: {options}")
        return options

    @app.callback(
        [Output('region-dropdown', 'value'),
         Output('departement-dropdown', 'value'),
         Output('etablissement-dropdown', 'value'),
         Output('type-dropdown', 'value')],
        [Input('reset-button', 'n_clicks')]
    )
    def reset_dropdowns(n_clicks):
        if n_clicks and n_clicks > 0:
            return None, None, None, None
        return no_update, no_update, no_update, no_update

    @app.callback(
        [Output('map', 'children'),
         Output('map', 'center'),
         Output('map', 'zoom'),
         Output('recap', 'children')],
        [Input('region-dropdown', 'value'),
         Input('departement-dropdown', 'value'),
         Input('etablissement-dropdown', 'value'),
         Input('type-dropdown', 'value'),
         Input('reset-button', 'n_clicks')]
    )
    def update_map(selected_region, selected_departement, selected_etablissement, selected_type, n_reset_clicks):
        global df_global
        print(f"update_map called with region: {selected_region}, department: {selected_departement}, establishment: {selected_etablissement}, type: {selected_type}, reset_clicks: {n_reset_clicks}")
        
        markers = []
        center = [46.603354, 1.888334]  # Default center on France
        zoom = 6
        recap = html.Div([
            html.Img(src='/assets/logo.png', style={'height': '50px'}),
            html.H2("France"),
            html.P("Sélectionnez une région, un département ou un établissement pour voir les détails.")
        ])

        filtered_df = df_global.copy()

        # Filtrer les données en fonction des sélections
        if selected_region:
            if isinstance(selected_region, list):
                filtered_df = filtered_df[filtered_df['Région'].isin(selected_region)]
            else:
                filtered_df = filtered_df[filtered_df['Région'] == selected_region]
            if not filtered_df.empty:
                center = [filtered_df.iloc[0]['Latitude'], filtered_df.iloc[0]['Longitude']]
                recap = html.Div([
                    html.Img(src='/assets/logo.png', style={'height': '50px'}),
                    html.H2(selected_region),
                    html.P(f"Nombre d'établissements: {len(filtered_df)}")
                ])
            zoom = 6
            markers = [
                dl.Marker(position=[row['Latitude'], row['Longitude']],
                          children=dl.Popup(html.Div([
                              html.Img(src='/assets/logo.png', style={'height': '50px'}),
                              html.H2(row['Nom de l\'établissement']),
                              html.P(f"Capacité: {row['Capacité']}"),
                              html.P(f"Description: {row['Description']}"),
                              html.P(f"Région: {row['Région']}"),
                              html.P(f"Département: {row['Département']}"),
                              html.A("Visiter le site", href=row.get('Website', '#'), target="_blank")
                          ], className="info-div-content")))
                for index, row in filtered_df.iterrows()
            ]
            markers = dl.LayerGroup(children=markers)

        if selected_departement:
            if isinstance(selected_departement, list):
                filtered_df = filtered_df[filtered_df['Département'].isin(selected_departement)]
            else:
                filtered_df = filtered_df[filtered_df['Département'] == selected_departement]
            if not filtered_df.empty:
                center = [filtered_df.iloc[0]['Latitude'], filtered_df.iloc[0]['Longitude']]
                recap = html.Div([
                    html.Img(src='/assets/logo.png', style={'height': '50px'}),
                    html.H2(selected_departement),
                    html.P(f"Nombre d'établissements: {len(filtered_df)}")
                ])
            zoom = 10
            markers = [
                dl.Marker(position=[row['Latitude'], row['Longitude']],
                          children=dl.Popup(html.Div([
                              html.Img(src='/assets/logo.png', style={'height': '50px'}),
                              html.H2(row['Nom de l\'établissement']),
                              html.P(f"Capacité: {row['Capacité']}"),
                              html.P(f"Description: {row['Description']}"),
                              html.P(f"Région: {row['Région']}"),
                              html.P(f"Département: {row['Département']}"),
                              html.A("Visiter le site", href=row.get('Website', '#'), target="_blank")
                          ], className="info-div-content")))
                for index, row in filtered_df.iterrows()
            ]
            markers = dl.LayerGroup(children=markers)

        if selected_type:
            if isinstance(selected_type, list):
                filtered_df = filtered_df[filtered_df['Type d\'établissement'].isin(selected_type)]
            else:
                filtered_df = filtered_df[filtered_df['Type d\'établissement'] == selected_type]
            if not filtered_df.empty:
                center = [filtered_df.iloc[0]['Latitude'], filtered_df.iloc[0]['Longitude']]
                recap = html.Div([
                    html.Img(src='/assets/logo.png', style={'height': '50px'}),
                    html.H2(selected_type),
                    html.P(f"Nombre d'établissements: {len(filtered_df)}")
                ])
            zoom = 12
            markers = [
                dl.Marker(position=[row['Latitude'], row['Longitude']],
                          children=dl.Popup(html.Div([
                              html.Img(src='/assets/logo.png', style={'height': '50px'}),
                              html.H2(row['Nom de l\'établissement']),
                              html.P(f"Capacité: {row['Capacité']}"),
                              html.P(f"Description: {row['Description']}"),
                              html.P(f"Région: {row['Région']}"),
                              html.P(f"Département: {row['Département']}"),
                              html.A("Visiter le site", href=row.get('Website', '#'), target="_blank")
                          ], className="info-div-content")))
                for index, row in filtered_df.iterrows()
            ]
            markers = dl.LayerGroup(children=markers)

        if selected_etablissement:
            if isinstance(selected_etablissement, list):
                filtered_df = filtered_df[filtered_df['Nom de l\'établissement'].isin(selected_etablissement)]
            else:
                filtered_df = filtered_df[filtered_df['Nom de l\'établissement'] == selected_etablissement]
            if not filtered_df.empty:
                center = [filtered_df.iloc[0]['Latitude'], filtered_df.iloc[0]['Longitude']]
                recap = html.Div([
                    html.Img(src='/assets/logo.png', style={'height': '50px'}),
                    html.H2(selected_etablissement),
                    html.P(f"Capacité: {filtered_df.iloc[0]['Capacité']}"),
                    html.P(f"Description: {filtered_df.iloc[0]['Description']}"),
                    html.P(f"Région: {filtered_df.iloc[0]['Région']}"),
                    html.P(f"Département: {filtered_df.iloc[0]['Département']}"),
                    html.A("Visiter le site", href=filtered_df.iloc[0].get('Website', '#'), target="_blank")
                ])
            zoom = 14
            markers = [
                dl.Marker(position=[row['Latitude'], row['Longitude']],
                          children=dl.Popup(html.Div([
                              html.Img(src='/assets/logo.png', style={'height': '50px'}),
                              html.H2(row['Nom de l\'établissement']),
                              html.P(f"Capacité: {row['Capacité']}"),
                              html.P(f"Description: {row['Description']}"),
                              html.P(f"Région: {row['Région']}"),
                              html.P(f"Département: {row['Département']}"),
                              html.A("Visiter le site", href=row.get('Website', '#'), target="_blank")
                          ], className="info-div-content")))
                for index, row in filtered_df.iterrows()
            ]
            markers = dl.LayerGroup(children=markers)

        if not markers:
            return [dl.TileLayer()], center, zoom, recap
        
        return [dl.TileLayer()] + [markers], center, zoom, recap

    @app.callback(
        Output('update-output', 'children'),
        [Input('update-button', 'n_clicks')],
        [State('region-dropdown', 'value'),
         State('departement-dropdown', 'value'),
         State('etablissement-dropdown', 'value'),
         State('type-dropdown', 'value')]
    )
    def update_data_callback(n_clicks, selected_region, selected_departement, selected_etablissement, selected_type):
        if n_clicks and n_clicks > 0:
            update_output = []
            try:
                if selected_etablissement:
                    # Mettre à jour les données pour un établissement spécifique
                    df_to_update = df_global[df_global['Nom de l\'établissement'] == selected_etablissement]
                elif selected_departement:
                    # Mettre à jour les données pour un département spécifique
                    df_to_update = df_global[df_global['Département'] == selected_departement]
                elif selected_type:
                    # Mettre à jour les données pour un type spécifique
                    df_to_update = df_global[df_global['Type d\'établissement'] == selected_type]
                elif selected_region:
                    # Mettre à jour les données pour une région spécifique
                    df_to_update = df_global[df_global['Région'] == selected_region]
                else:
                    # Mettre à jour toutes les données
                    df_to_update = df_global

                new_data = load_new_data(chemin_nouveau_fichier)
                df_updated, changes = update_data(df_to_update, new_data)
                save_data(df_updated, chemin_fichier)
                update_output.append(f"Les données ont été mises à jour avec les changements suivants: {', '.join(changes)}")
            except Exception as e:
                update_output.append(f"Erreur lors de la mise à jour des données: {str(e)}")
            return update_output
        return ""

    @app.callback(
        Output('scrape-output', 'children'),
        [Input('search-button', 'n_clicks')],
        [State('region-dropdown', 'value'),
         State('departement-dropdown', 'value'),
         State('etablissement-dropdown', 'value'),
         State('type-dropdown', 'value')]
    )
    def scrape_data_callback(n_clicks, selected_region, selected_departement, selected_etablissement, selected_type):
        if n_clicks and n_clicks > 0:
            try:
                if selected_etablissement:
                    # Scraper les données pour un établissement spécifique
                    df_to_scrape = df_global[df_global['Nom de l\'établissement'] == selected_etablissement]
                elif selected_departement:
                    # Scraper les données pour un département spécifique
                    df_to_scrape = df_global[df_global['Département'] == selected_departement]
                elif selected_type:
                    # Scraper les données pour un type spécifique
                    df_to_scrape = df_global[df_global['Type d\'établissement'] == selected_type]
                elif selected_region:
                    # Scraper les données pour une région spécifique
                    df_to_scrape = df_global[df_global['Région'] == selected_region]
                else:
                    # Scraper toutes les données
                    df_to_scrape = df_global

                def update_progress(current_value, total_value):
                    print(f"Progress: {current_value}/{total_value}")

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                scraped_df, changes = loop.run_until_complete(scrape_data_async(df_to_scrape, update_progress))
                loop.close()

                # Appliquer la fonction de nettoyage après le scraping
                scraped_df['Capacité'] = scraped_df['Capacité'].apply(clean_capacity)

                # Assurez-vous que les index correspondent
                scraped_df = scraped_df.set_index(df_to_scrape.index)

                # Mettez à jour df_global avec les nouvelles données scrappées
                print("Mise à jour de df_global avec les nouvelles données scrappées")
                df_global.update(scraped_df)
                # Sauvegardez les nouvelles données dans le fichier
                print("Sauvegarde des nouvelles données dans le fichier")
                save_data(df_global, chemin_fichier)
                print(f"Scraping terminé avec les changements suivants: {', '.join(changes)}")
                return [html.Div(f"Scraping terminé avec les changements suivants: {', '.join(changes)}")]
            except Exception as e:
                print(f"Erreur lors du scraping des données: {str(e)}")
                return [html.Div(f"Erreur lors du scraping des données: {str(e)}")]
        return [html.Div("Scraping non déclenché")]

    @app.callback(
        Output('toast-container', 'children'),
        [Input('update-button', 'n_clicks'),
         Input('search-button', 'n_clicks')],
        [State('region-dropdown', 'value'),
         State('departement-dropdown', 'value'),
         State('etablissement-dropdown', 'value'),
         State('type-dropdown', 'value')]
    )
    def show_toast(n_update_clicks, n_search_clicks, selected_region, selected_departement, selected_etablissement, selected_type):
        ctx = callback_context
        if not ctx.triggered:
            return ""
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'update-button' and n_update_clicks and n_update_clicks > 0:
            return dbc.Toast(
                "Les données ont été mises à jour avec succès.",
                id="update-toast",
                header="Mise à jour",
                icon="success",
                duration=4000,
            )

        if button_id == 'search-button' and n_search_clicks and n_search_clicks > 0:
            return dbc.Toast(
                "Recherche en cours...",
                id="search-toast",
                header="Recherche",
                icon="info",
                duration=4000,
            )

        return ""
