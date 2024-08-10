import os
import streamlit as st
from dotenv import dotenv_values

CONFIG_DIR = "config_files"
FIELDS_FILE = os.path.join(CONFIG_DIR, "needed_fields.txt")

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
        if filename.endswith(".env"):
            bot_name = filename.replace(".env", "")
            bots[bot_name] = dotenv_values(os.path.join(CONFIG_DIR, filename))
    return bots

st.set_page_config(page_title="New Chatbots", page_icon="📈")

st.title("ShreckBots – Create New Chat Bot")

needed_fields = load_needed_fields()
bots = load_bot_configs()
bot_names = list(bots.keys())

st.subheader("Create a New Chat Bot")
new_bot_name = st.text_input("New Bot Name")
new_bot_config = {}

if new_bot_name:
    if new_bot_name in bot_names:
        st.error("Bot name already exists. Please choose a different name.")
    else:
        all_filled = True
        for field, description in needed_fields:
            value = st.text_area(f"{field} ({description})")
            new_bot_config[f"{field}_{new_bot_name}"] = value
            if not value:
                all_filled = False
        
        if st.button("Create Bot") and all_filled:
            save_bot_config(new_bot_name, new_bot_config)
            st.success(f"Bot '{new_bot_name}' created successfully!")
            st.rerun()  # Reset the form after creation