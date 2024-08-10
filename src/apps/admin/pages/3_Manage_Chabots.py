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

def load_bot_configs():
    bots = {}
    for filename in os.listdir(CONFIG_DIR):
        if filename.endswith(".env") and filename != "api.env":
            bot_name = filename.replace(".env", "")
            bots[bot_name] = dotenv_values(os.path.join(CONFIG_DIR, filename))
    return bots

def save_bot_config(bot_name, config):
    filepath = os.path.join(CONFIG_DIR, f"{bot_name}.env")
    with open(filepath, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}='{value}'\n")

def delete_bot_config(bot_name):
    filepath = os.path.join(CONFIG_DIR, f"{bot_name}.env")
    if os.path.exists(filepath):
        os.remove(filepath)


st.set_page_config(page_title="Manage Chatbots", page_icon="🤖")


st.title("ShreckBots – Edit Chat Bot")

needed_fields = load_needed_fields()
bots = load_bot_configs()
bot_names = list(bots.keys())

if 'selected_bot' not in st.session_state:
    st.session_state['selected_bot'] = None

# Bot Selection in Sidebar
st.sidebar.subheader("Select a Bot to Edit")
selected_bot = st.sidebar.radio("Available Bots", bot_names)

if selected_bot:
    st.session_state['selected_bot'] = selected_bot

# Bot Editing
if st.session_state['selected_bot']:
    st.subheader(f"Editing: {st.session_state['selected_bot']}")
    config = bots[st.session_state['selected_bot']]
    updated_config = {}
    all_filled = True
    for field, description in needed_fields:
        value = st.text_area(f"{field} ({description})", config.get(f"{field}_{st.session_state['selected_bot']}", ""))
        updated_config[f"{field}_{st.session_state['selected_bot']}"] = value
        if not value:
            all_filled = False
    
    if st.button("Update Bot") and all_filled:
        save_bot_config(st.session_state['selected_bot'], updated_config)
        st.success(f"{st.session_state['selected_bot']} updated successfully.")
    
    if st.button("Delete Bot"):
        delete_bot_config(st.session_state['selected_bot'])
        st.success(f"{st.session_state['selected_bot']} deleted successfully.")
        st.session_state['selected_bot'] = None
        st.experimental_rerun()