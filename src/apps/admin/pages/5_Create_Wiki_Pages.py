import os
import streamlit as st
import requests
from dotenv import load_dotenv, dotenv_values
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import time

CONFIG_DIR = "config_files"
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

st.set_page_config(page_title="Update Wiki Pages", page_icon="📈")

st.title("ShreckBots – Update Wiki Pages")

st.markdown("---")
st.write("""This page allows you to create and update wiki pages automatically based on a given text.
         I will read the text, and following the parameters of each bot, I will propose new pages
         that can be added to the wiki, or new content to update existing pages.
         """)
st.write("First, select the bot you want to create pages to.")
st.write("Second, select the text you want me to read.")
st.write("Third, click on the Update Wiki button and I will do my magic!")
st.write("I will tell you when everything is ready, and you can use the Upload Wiki Pages tool to continue.")
st.write("Need more information? Check our Shreckbot manual: https://github.com/pablovin/Shreckbots")

st.markdown("---")

load_dotenv(API_CONFIG_FILE)
bots = load_bot_configs()
bot_names = list(bots.keys())

if not bot_names:
    st.sidebar.write("No chat bots available.")
else:
    selected_bot_name = st.sidebar.selectbox("Select a bot", bot_names)
    if selected_bot_name:
        config_bot = bots[selected_bot_name].get(f'WIKI_API_URL_{selected_bot_name}')
        st.sidebar.write(f"WIKI_API_URL: {config_bot}")

        uploaded_file = st.sidebar.file_uploader("Choose a file (.pdf or .txt)", type=["pdf", "txt"])

        if st.sidebar.button("Update Wiki Pages"):
            if uploaded_file is not None:
                file_content = extract_text_from_file(uploaded_file)
                response = requests.post(
                    f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/get_new_wiki_pages",
                    json={"bot": selected_bot_name, "text": file_content}
                )
                if response.status_code == 200:
                    st.session_state['selected_bot'] = selected_bot_name
                    st.session_state['show_log'] = True
                    st.rerun()
                else:
                    st.error("Failed to create wiki pages.")
            else:
                st.error("Please upload a file before updating the wiki pages.")

if 'show_log' in st.session_state and st.session_state['show_log']:
    st.subheader("Operation Outcome")
    log_file_path = 'update_log.log'
    log_contents = st.empty()
    stop_logging = False

    while not stop_logging:
        content = read_log_contents(log_file_path)
        log_contents.text(content)
        if " --- Update Done!" in content:
            stop_logging = True
        time.sleep(1)

    st.success("Wiki pages created and ready to be uploaded!")