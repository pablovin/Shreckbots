import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values

CONFIG_DIR = "config_files"
API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")

def load_api_config():
    if os.path.exists(API_CONFIG_FILE):
        return dotenv_values(API_CONFIG_FILE)
    return {}

def save_api_config(config):
    with open(API_CONFIG_FILE, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}='{value}'\n")

st.set_page_config(page_title="Shreckbot Configurations", page_icon="📈")
st.title("ShreckBots – API Configurations")

api_config = load_api_config()

if not api_config:
    st.write("No API configurations found.")
 
else:
    st.subheader("Edit API Configurations")
    api_config_updated = {}
    all_filled = True

    for key, value in api_config.items():
        updated_value = st.text_area(key, value)
        api_config_updated[key] = updated_value
        if not updated_value:
            all_filled = False

    if st.button("Update API Configurations"):
        if all_filled:
            save_api_config(api_config_updated)
            st.success("API config updated successfully.")
        else:
            st.error("All fields must be filled.")
