import hashlib
import os
import aiofiles
import logging
import feedparser
import requests
from bs4 import BeautifulSoup
import re
import json

LAST_ENTRY_DIR = 'last_entry'

# Assurer la création du répertoire last_entry
if not os.path.exists(LAST_ENTRY_DIR):
    os.makedirs(LAST_ENTRY_DIR)

# Lire les URLs des flux RSS depuis un fichier json dans le dossier 'urls'
def read_rss_urls_from_json(json_file):
    try:
        logging.info(f"Attempting to read RSS URLs from {json_file}")
        with open(json_file, 'r') as file:
            data = json.load(file)
            urls = data.get("urls", [])
            logging.info(f"Successfully read URLs: {urls}")
            return urls
    except FileNotFoundError:
        logging.error(f"RSS URLs JSON file not found: {json_file}")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Error reading RSS URLs JSON file {json_file}: {e}")
        return []

def get_hashed_filename(feed_url):
    return hashlib.md5(feed_url.encode('utf-8')).hexdigest()

def get_rss_feed(url):
    feed = feedparser.parse(url)
    return feed.entries

async def read_last_entry(feed_url):
    filename = get_hashed_filename(feed_url) + '.txt'
    file_path = os.path.join(LAST_ENTRY_DIR, filename)
    
    try:
        async with aiofiles.open(file_path, 'r') as file:
            last_entries = await file.read()
            last_entries_list = last_entries.strip().split(',')  # Suppression des espaces blancs et division
            logging.info(f"Read last entries IDs for {feed_url}: {last_entries_list}")
            return last_entries_list
    except FileNotFoundError:
        logging.warning(f"Last entry file for {feed_url} not found.")
        return []

async def write_last_entry(feed_url, entry_titles):
    filename = get_hashed_filename(feed_url) + '.txt'
    file_path = os.path.join(LAST_ENTRY_DIR, filename)
    
    async with aiofiles.open(file_path, 'w') as file:
        await file.write(','.join(entry_titles).strip())  # Sauvegarder les titres séparés par une virgule
        logging.info(f"Wrote last entry titles for {feed_url}: {entry_titles} in file {file_path}")

def normalize_title(title):
    """Supprimer les résolutions (720p, 1080p, 4K, 4k, etc.) pour la comparaison des titres."""
    # Le pattern cherche les résolutions 720p, 1080p, etc., ainsi que 4K ou 4k, de manière insensible à la casse
    return re.sub(r'\s*(\d{3,4}p|4k)\s*', '', title, flags=re.IGNORECASE).strip()

def scrape_file_name_and_title(entry_url):
    try:
        # Assure-toi de remplacer le chemin de l'URL et de retirer le .torrent
        if entry_url.endswith('.torrent'):
            entry_url = entry_url.replace('/download/', '/view/').replace('.torrent', '')

        response = requests.get(entry_url)
        response.raise_for_status()  # Vérifie que la requête a réussi

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Trouve la div avec l'id 'torrent-description'
        episode_title = None
        audio_languages = None
        description_section = soup.find('div', {'id': 'torrent-description', 'class': 'panel-body'})
        
        if description_section:
            # Extraction du texte Markdown du titre
            markdown_text = description_section.get_text(strip=True)
            
            # Recherche du titre dans le format Markdown
            match_title = re.search(r'\[\*\*(.*?)\*\*\]', markdown_text)
            if match_title:
                full_title = match_title.group(1)
                # Utilisation d'une expression régulière pour extraire la partie souhaitée
                episode_title_match = re.search(r'S\d{2}E\d{2}\s+(.*)', full_title)
                if episode_title_match:
                    episode_title = episode_title_match.group(1).strip()
                logging.debug(f"Episode title found: {episode_title}")

            # Recherche des langues audio dans le texte
            match_audio = re.search(r'\*\*Audio\*\*:\s*(.*?)(\n|$)', markdown_text)
            if match_audio:
                audio_raw = match_audio.group(1)
                # Extraction des langues uniquement (ex : "French (France)" devient "French")
                audio_languages = ', '.join([lang.split(' ')[0] for lang in audio_raw.split(',')])
                logging.debug(f"Audio languages found: {audio_languages}")
            else:
                logging.debug(f"Could not find the audio information in {entry_url}")
        else:
            logging.debug(f"Could not find the div with id 'torrent-description' in {entry_url}")

        # Trouve la div avec la classe spécifique pour le nom du fichier
        file_list_section = soup.find('div', class_='torrent-file-list panel-body')
        if file_list_section:
            file_name = file_list_section.find('li').get_text(strip=True)
            return file_name, episode_title, audio_languages
        else:
            logging.warning(f"Could not find file list section in {entry_url}")
            return None, episode_title, audio_languages
    except requests.RequestException as e:
        logging.error(f"Error fetching the page {entry_url}: {e}")
        return None, None, None





