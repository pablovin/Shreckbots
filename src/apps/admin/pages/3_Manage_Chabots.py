import os
import streamlit as st
from utils_admin import load_needed_fields, save_bot_config, load_bot_configs, delete_bot_config

CONFIG_DIR = "config_files"
FIELDS_FILE = os.path.join(CONFIG_DIR, "needed_fields.txt")

st.set_page_config(page_title="Manage Chatbots", page_icon="🤖")

st.title("ShreckBots – Edit Chat Bot")
st.markdown("---")
st.write("Use the panel on the right to select a bot to manage!")
st.markdown("---")

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