# state_manager.py

import json
import os
import logging

STATE_FILE_PATH = 'state/groups_state.json'

# Assurer la création du répertoire et du fichier de sauvegarde
if not os.path.exists('state'):
    os.makedirs('state')

if not os.path.exists(STATE_FILE_PATH):
    with open(STATE_FILE_PATH, 'w') as file:
        json.dump({}, file)

def read_group_states():
    try:
        with open(STATE_FILE_PATH, 'r') as file:
            group_states = json.load(file)
            logging.info(f"Loaded group states from {STATE_FILE_PATH}")
            return group_states
    except Exception as e:
        logging.error(f"Failed to read group states: {e}")
        return {}

def write_group_states(group_states):
    try:
        with open(STATE_FILE_PATH, 'w') as file:
            json.dump(group_states, file)
            logging.info(f"Group states saved to {STATE_FILE_PATH}")
    except Exception as e:
        logging.error(f"Failed to write group states: {e}")

def update_group_state(feed_url, group_title, state):
    group_states = read_group_states()
    if feed_url not in group_states:
        group_states[feed_url] = {}
    group_states[feed_url][group_title] = state
    write_group_states(group_states)

def get_group_state(feed_url, group_title):
    group_states = read_group_states()
    if feed_url in group_states:
        return group_states[feed_url].get(group_title, False)
    return False

