import os
from dotenv import load_dotenv, dotenv_values
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup

CONFIG_DIR = "config_files"
API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")

FIELDS_FILE = os.path.join(CONFIG_DIR, "needed_fields.txt")


#ADMING CONFIG FUNCTIONS
def load_api_config():
    if os.path.exists(API_CONFIG_FILE):
        load_dotenv(API_CONFIG_FILE)
        return dotenv_values(API_CONFIG_FILE)
    return {}


def save_api_config(config):
    with open(API_CONFIG_FILE, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}='{value}'\n")

#BOT CONFIG FUNCTIONS
def load_needed_fields():
    fields = []
    if os.path.exists(FIELDS_FILE):
        with open(FIELDS_FILE, 'r') as f:
            for line in f:
                if ',' in line:
                    field, description = line.strip().split(',', 1)
                    fields.append((field.strip(), description.strip()))
    return fields

def save_bot_config(bot_name, config):
    filepath = os.path.join(CONFIG_DIR, f"{bot_name}.env")
    with open(filepath, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}='{value}'\n")

def load_bot_configs():
    bots = {}
    for filename in os.listdir(CONFIG_DIR):
        if filename.endswith(".env") and filename != "api.env":
            bot_name = filename.replace(".env", "")
            bots[bot_name] = dotenv_values(os.path.join(CONFIG_DIR, filename))
    return bots


def delete_bot_config(bot_name):
    filepath = os.path.join(CONFIG_DIR, f"{bot_name}.env")
    if os.path.exists(filepath):
        os.remove(filepath)


#UPDATE_LOG CONTENT

def read_log_contents(log_file_path):
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as f:
            return f.read()
    return ""


#UPLOADED FILE
def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    elif uploaded_file.type == "text/html":
        soup = BeautifulSoup(uploaded_file.read(), "html.parser")
        text = soup.get_text()
    else:
        text = uploaded_file.read().decode("utf-8")
    return text


#Wiki Folder

def get_files_in_wiki_folder(folder_path):
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]