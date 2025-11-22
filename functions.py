import os
import json
import requests

config_path = 'config.json'

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = json.load(file)
    
    return config

def save_config(config_data, config_path):
    with open(config_path, 'w') as file:
        json.dump(config_data, file, indent=4)

# Function to add a value to the list
def add_to_list(key, value):
    with open(config_path, 'r') as file:
        data = json.load(file)
    
    if key in data and isinstance(data[key], list):
        data[key].append(value)
        
        with open(config_path, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    else:
        print(f"Key '{key}' not found or is not a list.")
        return False

# Function to save history
def save_history(channel_id, interaction):
    try:
        with open(config_path, 'r') as file:
            data = json.load(file)
    except Exception:
        data = {}
        
    if "history" not in data:
        data["history"] = {}
        
    if channel_id not in data["history"]:
        data["history"][channel_id] = []
        
    data["history"][channel_id].append(interaction)
    
    # Limit to last 6
    if len(data["history"][channel_id]) > 6:
        data["history"][channel_id] = data["history"][channel_id][-6:]
        
    with open(config_path, 'w') as file:
        json.dump(data, file, indent=4)

def get_history(channel_id):
    try:
        with open(config_path, 'r') as file:
            data = json.load(file)
    except Exception:
        data = {}
    
    if "history" not in data:
        data["history"] = {}
    
    if channel_id not in data["history"]:
        data["history"][channel_id] = []
    
    return data["history"][channel_id]

def access_api(url, parameter, error_message, headers=None):
    if headers:
        raw = requests.get(url, headers=headers)
    else:
        raw = requests.get(url)
    if raw.status_code == 200:
        try:
            data = raw.json()
            response = data[parameter]
        except (requests.exceptions.JSONDecodeError, KeyError):
            response = str(f"{error_message}")
        except Exception as e:
            response = str(f"{error_message} (Error {str(e)})")
    else:
        response = str(f"{error_message} (HTTP {raw.status_code})")
    
    return response