import os
from dotenv import load_dotenv
import logging

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))  # Assurez-vous que l'ID du canal est un entier

# Lecture de la variable DEBUG_MODE à partir du fichier .env
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

if DEBUG_MODE:
    # Création du répertoire logs si nécessaire
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configuration des logs pour le mode DEBUG
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(message)s',
        filename='logs/bot.log',
        filemode='a'
    )
    logging.info("Logging is set to DEBUG mode.")
else:
    # Configuration des logs pour ignorer tous les messages
    logging.getLogger().addHandler(logging.NullHandler())
    logging.info("Logging is disabled in production mode.")
