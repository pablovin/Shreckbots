import os
import streamlit as st
import requests
from dotenv import load_dotenv
from dotenv import dotenv_values
import time


CONFIG_DIR = "config_files"
LOG_FILE_PATH = "update_log.log"

API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")

def load_bot_configs():
    bots = {}
    for filename in os.listdir(CONFIG_DIR):
        if filename.endswith(".env") and filename != "api.env":
            bot_name = filename.replace(".env", "")
            bots[bot_name] = dotenv_values(os.path.join(CONFIG_DIR, filename))
    return bots

def read_log_contents(log_file_path):
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as f:
            return f.read()
    return ""


st.set_page_config(page_title="Update Bot Embeddings", page_icon="📈")

st.title("ShreckBots – Update Chat Embeddings")

load_dotenv(API_CONFIG_FILE)
bots = load_bot_configs()
bot_names = list(bots.keys())

if not bot_names:
    st.write("No chat bots available.")
else:

    st.subheader("Update Embeddings for Chat Bots")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("Bot")
    with col2:
        st.subheader("Wiki Pages")            
    with col3:
        st.subheader("Wiki Embeddings")                        
    with col4:
        st.subheader("Document Embeddings")                                    

    selected_action = None
    selected_bot_name = None

    for bot_name in bot_names:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.subheader(f"{bot_name}")      

        with col2:
            if st.button(f"Read Wiki", key=f"read_wiki_{bot_name}"):
                selected_action = "read_wiki"
                selected_bot_name = bot_name

        with col3:
            if st.button(f"Update Wiki", key=f"update_wiki_{bot_name}"):
                selected_action = "update_wiki"
                selected_bot_name = bot_name

        with col4:
            if st.button(f"Update Documents", key=f"update_document_{bot_name}"):
                selected_action = "update_document"
                selected_bot_name = bot_name

    if selected_action and selected_bot_name:
        if selected_action == "read_wiki":
            response = requests.post(f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/read_wiki", json={"bot": selected_bot_name})
        elif selected_action == "update_wiki":
            response = requests.post(f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/update_embedding", json={"bot": selected_bot_name, "folder": "wiki"})
        elif selected_action == "update_document":
            response = requests.post(f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/update_embedding", json={"bot": selected_bot_name, "folder": "books"})

        if response.status_code == 200:

            st.success(f"{selected_action.replace('_', ' ').capitalize()} initiated for {selected_bot_name}.")
            st.subheader("Operation Outcome")
            log_contents = st.empty()
            stop_logging = False

            while not stop_logging:
                content = read_log_contents(LOG_FILE_PATH)
                log_contents.text(content)
                if "--- Update Done!" in content:
                    stop_logging = True
                time.sleep(1)

            st.success("Operation completed successfully!")
        else:
            st.error(f"Failed to perform {selected_action.replace('_', ' ').capitalize()} for {selected_bot_name}.")