from dotenv import load_dotenv
import os

CONFIG_DIR = "config_files"

def load_shreckbot_config():
    
    API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")
    load_dotenv(API_CONFIG_FILE)
    
def load_bot_config(bot):
    
    config_file_bot = os.path.join(CONFIG_DIR, f"{bot}.env")
    load_dotenv(config_file_bot)  
