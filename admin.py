import streamlit as st
import os
import requests
from dotenv import dotenv_values, set_key, unset_key, load_dotenv
import time

CONFIG_DIR = "config_files"
FIELDS_FILE = os.path.join(CONFIG_DIR, "needed_fields.txt")
API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")

API_HOST = "localhost"  # Change to your API host
API_PORT = 5000  # Change to your API port

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

def load_api_config():
    if os.path.exists(API_CONFIG_FILE):
        return dotenv_values(API_CONFIG_FILE)
    return {}

def save_bot_config(bot_name, config):
    filepath = os.path.join(CONFIG_DIR, f"{bot_name}.env")
    with open(filepath, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}='{value}'\n")

def save_api_config(config):
    with open(API_CONFIG_FILE, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}='{value}'\n")

def delete_bot_config(bot_name):
    filepath = os.path.join(CONFIG_DIR, f"{bot_name}.env")
    if os.path.exists(filepath):
        os.remove(filepath)

def read_log_contents(log_file_path):
    with open(log_file_path, 'r') as f:
        content = f.read()
    return content

def main():
    st.title("ShreckBots – Admin Page")
    
    needed_fields = load_needed_fields()
    bots = load_bot_configs()
    bot_names = list(bots.keys())
    api_config = load_api_config()
    
    if 'creating_new_bot' not in st.session_state:
        st.session_state['creating_new_bot'] = False
    if 'api_config' not in st.session_state:
        st.session_state['api_config'] = False
    if 'read_wiki' not in st.session_state:
        st.session_state['read_wiki'] = False
    if 'update_embeddings' not in st.session_state:
        st.session_state['update_embeddings'] = False

    st.sidebar.subheader("Available Chat Bots")
    if not bot_names:
        st.sidebar.write("No chat bots available.")
    selected_bot = st.sidebar.radio("Select a bot", bot_names)

    if st.sidebar.button("Create New Chat Bot"):
        st.session_state['creating_new_bot'] = True
        st.session_state['api_config'] = False
        st.session_state['read_wiki'] = False
        st.session_state['update_embeddings'] = False
        st.rerun() 

    if st.sidebar.button("ShreckBot Configurations"):
        st.session_state['creating_new_bot'] = False
        st.session_state['api_config'] = True
        st.session_state['read_wiki'] = False
        st.session_state['update_embeddings'] = False
        st.rerun() 

    if st.sidebar.button("Read Wiki data"):
        st.session_state['creating_new_bot'] = False
        st.session_state['api_config'] = False
        st.session_state['read_wiki'] = True
        st.session_state['update_embeddings'] = False
        st.rerun() 

    if st.sidebar.button("Update Chat Embeddings"):
        st.session_state['creating_new_bot'] = False
        st.session_state['api_config'] = False
        st.session_state['read_wiki'] = False
        st.session_state['update_embeddings'] = True
        st.rerun() 

    if st.session_state['api_config']:
        st.subheader("ShreckBot Configurations")
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
                st.success("API config updated.")
            else:
                st.error("All fields must be filled.")
        
        if st.button("Back"):
            st.session_state['api_config'] = False
            st.rerun() 
    elif st.session_state['creating_new_bot']:
        st.subheader("Create New Chat Bot")
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
                
                if st.button("Create Chat Bot"):
                    if all_filled:
                        save_bot_config(new_bot_name, new_bot_config)
                        st.session_state['creating_new_bot'] = False
                        st.rerun() 
                    else:
                        st.error("All fields must be filled.")
        
        if st.button("Back"):
            st.session_state['creating_new_bot'] = False
            st.rerun() 
    elif st.session_state['read_wiki']:
        st.subheader("Read Wiki Data")
        load_dotenv(API_CONFIG_FILE)

        for bot_name in bot_names:
            if st.button(f"Update Wiki for {bot_name}"):
                response = requests.post(f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/read_wiki", json={"bot": bot_name})
                if response.status_code == 200:
                    st.session_state['selected_bot'] = bot_name
                    st.session_state['show_log'] = True
                    st.rerun() 

        if 'show_log' in st.session_state and st.session_state['show_log']:
            bot_name = st.session_state['selected_bot']
            log_file_path = 'update_log.log'
            st.text(f"Update Wiki for {bot_name}")
            log_contents = st.empty()
            stop_logging = False

            while not stop_logging:
                content = read_log_contents(log_file_path)
                log_contents.text(content)
                if " --- Update Done!" in content:
                    stop_logging = True
                time.sleep(1)
                
            st.button("Back", on_click=lambda: st.session_state.update({"show_log": False, "selected_bot": None}))

    elif st.session_state['update_embeddings']:
        st.subheader("Update Chat Embeddings")
        load_dotenv(API_CONFIG_FILE)

        for bot_name in bot_names:
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Update Wiki Embeddings for {bot_name}"):
                    response = requests.post(f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/update_embedding", json={"bot": bot_name, "folder": "wiki"})
                    if response.status_code == 200:
                        st.session_state['selected_bot'] = bot_name
                        st.session_state['show_log'] = True
                        st.rerun() 
            with col2:
                if st.button(f"Update Document Embeddings for {bot_name}"):
                    response = requests.post(f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/update_embedding", json={"bot": bot_name, "folder": "books"})
                    if response.status_code == 200:
                        st.session_state['selected_bot'] = bot_name
                        st.session_state['show_log'] = True
                        st.rerun() 

        if 'show_log' in st.session_state and st.session_state['show_log']:
            bot_name = st.session_state['selected_bot']
            log_file_path = 'update_log.log'
            st.text(f"Update Embeddings for {bot_name}")
            log_contents = st.empty()
            stop_logging = False

            while not stop_logging:
                content = read_log_contents(log_file_path)
                log_contents.text(content)
                if " --- Update Done!" in content:
                    stop_logging = True
                time.sleep(1)
                
            st.button("Back", on_click=lambda: st.session_state.update({"show_log": False, "selected_bot": None}))

    else:
        if selected_bot:
            st.subheader(f"Config for {selected_bot}")
            config = bots[selected_bot]
            display_config = {field: config.get(f"{field}_{selected_bot}", "") for field, _ in needed_fields}
            
            updated_config = {}
            all_filled = True
            for field, description in needed_fields:
                value = st.text_area(f"{field} ({description})", display_config[field])
                updated_config[f"{field}_{selected_bot}"] = value
                if not value:
                    all_filled = False
            
            if st.button("Update"):
                if all_filled:
                    save_bot_config(selected_bot, updated_config)
                    st.success("Bot config updated.")
                else:
                    st.error("All fields must be filled.")
            
            if st.button("Delete Chat Bot"):
                delete_bot_config(selected_bot)
                st.rerun() 

if __name__ == "__main__":
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    main()