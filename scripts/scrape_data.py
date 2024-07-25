import requests
from bs4 import BeautifulSoup
import pandas as pd
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import asyncio
import aiohttp

terms_to_search_description = [
    'âge', 'hebergement', 'accueil', 'accompagnements', 'centre', 'mecs', 'maison d\'enfant à caractère sociale',
    'AEMO', 'R : Action éducative en milieu ouvert renforcée', 'Justice', 'AET', 'Accueils éducatifs et thérapeutiques', 'Fondation',
    'AF', 'Assistant Familial', 'AJ', 'Aide juridictionnelle', 'AMP', 'Aide médico pédagogique', 'ANCV', 'Agence Nationale des Chèques Vacances',
    'ANESM', 'Agence nationale de l’évaluation et de la qualité des établissements et services sociaux et médico-sociaux', 'AP', 'Accueil provisoire',
    'APP', 'Analyse des pratiques professionnelles', 'ARS', 'Agence régionale de santé', 'ASS', 'Assistante de service social', 'ASE', 'Aide sociale à l’enfance',
    'AVS', 'Auxiliaire de vie scolaire', 'CAF', 'Caisse d’allocations familiales', 'CAFDES', 'Certificat d’aptitude aux fonctions de directeur d’établissement',
    'CAFERUIS', 'Certificat d’aptitude aux fonctions d’encadrement et de responsable d’unité d’intervention sociale', 'CAMSP', 'Centre d’action médico-sociale précoce',
    'CASF', 'Code de l’action sociale et des familles', 'CAVASEM', 'Centre d’accueil des victimes de violences sexuelles et de maltraitance', 'CCAS', 'Centre Communal d’Action Sociale',
    'CCN66', 'Convention collective nationale de 1966', 'CD', 'Conseil départemental', 'CDD', 'Contrat à durée déterminée', 'CDI', 'Contrat à durée indéterminée',
    'CDAPH', 'Commission des droits et de l’autonomie des personnes handicapées', 'CEF', 'Centre éducatif fermé', 'CEP', 'Conseil en évolution professionnelle',
    'CER', 'Centre éducatif renforcé', 'CESF', 'Conseiller en économie sociale et familiale', 'CHS', 'Centre hospitalier spécialisé', 'CHRS', 'Centre d’hébergement et réinsertion sociale',
    'CIO', 'Centre d’information et d’orientation', 'CLIS', 'Classe pour l’inclusion scolaire', 'CMP', 'Centre médico psychologique', 'CMPP', 'Centre médico psycho pédagogique',
    'CNIL', 'Commission nationale de l’informatique et des libertés', 'CPOM', 'Contrat pluriannuel d’objectifs et de moyens', 'CRIP', 'Cellule de recueil des informations préoccupantes',
    'CROSSMS', 'Comité régional de l’organisation du secteur social et médico-social', 'CROUS', 'Comité régional des œuvres universitaires et sociales', 'CSE', 'Comité social et économique',
    'CSTS', 'Conseil supérieur du travail social', 'CVS', 'Conseil de la Vie Sociale', 'DASES', 'Direction de l’action sanitaire et sociale', 'DDCS', 'Direction Départementale de la cohésion sociale',
    'DEAF', 'Diplôme d’Etat d’assistante familiale', 'DEASS', 'diplôme d’Etat d’assistant de service social', 'DEES', 'Diplôme d’Etat d’éducateur spécialisé', 'DEME', 'Diplôme d’Etat moniteur éducateur',
    'DGCS', 'Direction générale de la cohésion sociale', 'DIPEC', 'Document individuel de prise en charge', 'Décret 2003', 'Décret d’application budgétaire de la Loi 2002-2', 'DTPJJ', 'Direction territoriale de la protection judiciaire de la jeunesse',
    'DUERP', 'Document unique d’évaluation des risques professionnels', 'DUI', 'Dossier Unique Informatisé', 'EADP', 'Entretien annuel de développement professionnel', 'EJE', 'Éducateur de jeunes enfants',
    'EHPAD', 'Établissement d’hébergement pour personnes âgées dépendantes', 'ERP', 'Établissement Recevant du Public', 'ERPE', 'Espace Rencontre Parents-enfants', 'ES', 'Éducateur spécialisé',
    'ESAT', 'Établissement et service d’aide par le travail', 'ETP', 'Équivalent Temps Plein', 'ETS', 'Éducateur technique spécialisé', 'FJT', 'Foyer de Jeunes Travailleurs', 'GAP', 'Groupes d’analyse de la Pratique',
    'GVT', 'Glissement Vieillesse Technicité', 'IME', 'Institut médico éducatif', 'IMP', 'Institut médico pédagogique', 'IMPRO', 'Institut médico professionnel', 'IOE', 'Investigation d’orientation éducative',
    'IP', 'Information préoccupante', 'ITEP', 'Institut thérapeutique, éducatif et pédagogique', 'JAF', 'Juge aux affaires familiales', 'JE', 'Juge des enfants', 'JM', 'Jeune majeur', 'JORF', 'Journal Officiel de la République Française',
    'LVDA', 'Lieux de vie et d’accueil', 'MDPH', 'Maison départementale des personnes handicapées', 'MECS', 'Maison d’enfants à caractère social', 'MIE', 'Mineur isolé étranger', 'MNA', 'Mineur non accompagné',
    'MJIE', 'Mesure judiciaire d’investigation et d’évaluation', 'ODAS', 'Observatoire départemental de l’action sociale', 'ODPE', 'Observatoire départemental de la protection de l’enfance', 'ONPE', 'Observatoire national de la protection de l’enfance',
    'OPP', 'Ordonnance de placement provisoire', 'PAD', 'Placement à domicile', 'PJJ', 'Protection judiciaire de la jeunesse', 'PMI', 'Protection maternelle et infantile', 'PPA', 'Projet Personnalisé d’Accompagnement', 'PPE', 'Projet pour l’enfant',
    'PPI', 'Programmation Pluriannuelle d’investissements', 'PPS', 'Projet Personnalisé de Scolarisation', 'RBPP', 'Recommandations de bonnes pratiques professionnelles', 'REAAP', 'Réseau d’écoute, d’appui et d’accompagnement des parents',
    'REAJI', 'Renforcer l’autonomie des jeunes par l’insertion', 'RJ', 'Résidence jeune', 'RH', 'Ressources Humaines', 'SAEF', 'Service d’action éducative auprès des familles', 'SAEJ', 'Service d’action éducative de jour', 'SAF', 'Service d’accueil familial',
    'SAPMN', 'Service d’adaptation progressive en milieu naturel', 'SASEP', 'Service d’accompagnement social et éducatif', 'SAU', 'Service d’accueil d’urgence', 'SEAT', 'Service éducatif auprès du tribunal', 'SCOP', 'Société coopérative de production',
    'SEGPA', 'Section d’enseignement général et professionnel adapté', 'SESSAD', 'Service d’éducation et de soins spécialisés à domicile', 'SID', 'Service individualisé et diversifié', 'SPAJ', 'Service de soutien à la parentalité et d’accueil de jour',
    'SPEF', 'Service de protection de l’enfance et de la famille', 'TED', 'Troubles Envahissants du développement', 'TISF', 'Technicien de l’intervention sociale et familiale', 'TOC', 'Troubles obsessionnels compulsifs', 'TPE', 'Tribunal pour enfants',
    'ULIS', 'Unité localisée pour l’inclusion', 'UNIOPSS', 'Union nationale interfédérale des œuvres et organismes sanitaires et sociaux', 'UPI', 'Unité pédagogique d’intégration', 'URIOPSS', 'Union régionale interfédérale des œuvres et organismes sanitaires et sociaux',
    'URSSAF', 'Unité de recouvrement des cotisations de sécurité sociale et d’allocations familiales', 'UV', 'Unité de vie', 'VA', 'Visites accompagnées', 'VM', 'Visites médiatisées'
]

terms_to_search_capacity = ['place', 'nombre de places', 'mesure']

def clean_capacity(value):
    match = re.search(r'\d+', str(value))
    return int(match.group()) if match else None

async def fetch_pdf_text(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            pdf_data = await response.read()
            with fitz.open(stream=pdf_data, filetype="pdf") as pdf_document:
                text = ""
                for page in pdf_document:
                    text += page.get_text()
                    text += pdf_image_to_text(page)
            return text

async def fetch_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            return await response.text()

def pdf_image_to_text(page):
    text = ""
    image_list = page.get_images(full=True)
    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = page.get_pixmap(xref)
        image_bytes = base_image.tobytes()

        # Ouvrir l'image avec PIL
        image = Image.open(io.BytesIO(image_bytes))

        # Utiliser Tesseract pour faire l'OCR sur l'image
        text += pytesseract.image_to_string(image, lang='eng')

    return text

def extract_info_from_html(soup, row):
    description = row['Description']  # Valeur par défaut si non trouvée
    capacity = row['Capacité']  # Valeur par défaut si non trouvée
    age_range = ''
    mixed = ''

    # Rechercher les informations pertinentes dans la balise <meta> avec name="description"
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description:
        description += meta_description.get('content', '')

    # Rechercher les informations pertinentes dans la balise <meta> avec property="og:description"
    og_description = soup.find('meta', attrs={'property': 'og:description'})
    if og_description:
        description += og_description.get('content', '')

    # Rechercher les informations de capacité spécifiques au type d'établissement
    capacity_tags = soup.find_all(lambda tag: tag.name in ['div', 'li'] and any(term in tag.text.lower() for term in terms_to_search_capacity))
    relevant_capacity = []

    for tag in capacity_tags:
        if any(term in tag.text.lower() for term in terms_to_search_capacity):
            relevant_capacity.append(tag.text)

    if relevant_capacity:
        capacity_text = ', '.join(relevant_capacity)
        capacity = clean_capacity(capacity_text)

    # Rechercher les informations sur la tranche d'âge
    age_tag = soup.find(lambda tag: tag.name == 'li' and 'âge' in tag.text.lower())
    if age_tag:
        age_range = age_tag.text

    # Rechercher les informations sur le mixte
    mixed_tag = soup.find(lambda tag: tag.name == 'li' and 'mixte' in tag.text.lower())
    if mixed_tag:
        mixed = 'Établissement mixte'

    return description, capacity, age_range, mixed

def extract_info_from_text(text, row):
    description = row['Description']  # Valeur par défaut si non trouvée
    capacity = row['Capacité']  # Valeur par défaut si non trouvée
    age_range = ''
    mixed = ''

    # Logique pour extraire les informations pertinentes du texte
    lines = text.split('\n')

    for line in lines:
        if 'âge' in line.lower():
            age_range = line
        if 'mixte' in line.lower():
            mixed = 'Établissement mixte'
        if 'place' in line.lower() or 'nombre de places' in line.lower():
            if any(term in line.lower() for term in terms_to_search_capacity):
                capacity = clean_capacity(line)
        if any(term in line.lower() for term in terms_to_search_description):
            description += line

    return description, capacity, age_range, mixed

async def scrape_data_async(df, update_progress):
    changes = []
    scraped_data = []

    total_items = len(df)
    print(f"Nombre total d'éléments à scraper: {total_items}")

    tasks = []

    for index, (idx, row) in enumerate(df.iterrows(), 1):
        url = row['Website']
        print(f"Scraping {index}/{total_items}: {url}")
        if pd.isna(url):
            continue

        tasks.append((index, idx, row, url))

    async def scrape_task(index, idx, row, url):
        try:
            if url.endswith('.pdf'):
                text = await fetch_pdf_text(url)
                if not text:
                    return None

                description, capacity, age_range, mixed = extract_info_from_text(text, row)

            else:
                html_content = await fetch_html(url)
                if not html_content:
                    return None

                soup = BeautifulSoup(html_content, 'html.parser')
                description, capacity, age_range, mixed = extract_info_from_html(soup, row)

            updated_row = row.copy()

            if capacity != row['Capacité']:
                print(f"Capacité mise à jour pour {row['Nom de l\'établissement']}: {row['Capacité']} -> {capacity}")
                updated_row['Capacité'] = capacity
                changes.append(f"Capacité mise à jour pour {row['Nom de l\'établissement']}")

            if description.strip() != row['Description'].strip():
                print(f"Description mise à jour pour {row['Nom de l\'établissement']}: {row['Description']} -> {description.strip()}")
                updated_row['Description'] = description.strip()
                changes.append(f"Description mise à jour pour {row['Nom de l\'établissement']}")

            if age_range.strip():
                updated_row['Description'] += f" - {age_range.strip()}"
            if mixed.strip():
                updated_row['Description'] += f" - {mixed.strip()}"

            return updated_row

        except Exception as e:
            print(f"Erreur lors du scraping de {url}: {e}")
            return None

        finally:
            update_progress(index, total_items)

    results = await asyncio.gather(*(scrape_task(index, idx, row, url) for index, idx, row, url in tasks))

    for result in results:
        if result is not None:
            scraped_data.append(result.to_dict())

    if scraped_data:
        scraped_df = pd.DataFrame(scraped_data)
        return scraped_df, changes
    else:
        return df, changes

# Utiliser un exemple de dataframe pour tester
df = pd.DataFrame({
    'Nom de l\'établissement': ['Etablissement 1', 'Etablissement 2'],
    'Website': ['http://example.com/page1', 'http://example.com/page2'],
    'Description': ['', ''],
    'Capacité': [0, 0]
})

# Fonction pour mettre à jour la progression (peut être une simple impression dans ce cas)
def update_progress(index, total):
    print(f"Progression: {index}/{total}")

# Exécution de la fonction de scraping avec l'exemple de dataframe
loop = asyncio.get_event_loop()
scraped_df, changes = loop.run_until_complete(scrape_data_async(df, update_progress))

print(scraped_df)
print(changes)
