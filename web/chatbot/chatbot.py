import os
import requests
import streamlit as st
from dotenv import load_dotenv, dotenv_values
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import io

from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

load_dotenv(override=True)

CONFIG_DIR = "config_files"
API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")
load_dotenv(API_CONFIG_FILE)

def load_bot_configs():
    bots = []
    for filename in os.listdir(CONFIG_DIR):
        if filename.endswith(".env") and filename != "api.env":
            bot_name = filename.replace(".env", "")
            bots.append(bot_name)
    return bots

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

bots = load_bot_configs()
if "chat" in st.query_params and st.query_params["chat"] in bots:
    chat_name = st.query_params["chat"]
    this_bot_env = API_CONFIG_FILE = os.path.join(CONFIG_DIR, f"{chat_name}.env")
    load_dotenv(API_CONFIG_FILE)   

        
    CHATBOT_URL = f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/chat"
    WEBSITE_NAME =  os.getenv('WEBSITE_NAME')
    CHAT_OFICIAL_NAME =  os.getenv(f'NAME_{chat_name}')
    CHAT_LOGO =  os.getenv(f'CHABOT_LOGO_{chat_name}')
    CHAT_DESCRIPTION =  os.getenv(f'DESCRIPTION_{chat_name}')
    CHAT_WELCOME =  os.getenv(f'WELCOME_MESSAGE_{chat_name}')
    CHAT_INPUT_MESSAGE =  os.getenv(f'INPUT_PROMPT_TEXT_{chat_name}')
    CHAT_PROCESSING_MESSAGE =  os.getenv(f'PROCESSING_TEXT_{chat_name}')
    CHAT_ERROR_MESSAGE =  os.getenv(f'ERROR_TEXT_{chat_name}')
    
    WEBSITE_LOGO =  os.getenv(f'WEBSITE_LOGO')
    CONTACT_PERSON = os.getenv(f'CONTACT_PERSON')

    print (f"Chat Logo: {CHAT_LOGO}")
    st.set_page_config(page_title=f"{WEBSITE_NAME} - {CHAT_OFICIAL_NAME}", layout = 'wide', initial_sidebar_state = 'auto')

    ctx = get_script_run_ctx()
    session_id = ctx.session_id

    with st.sidebar:
        st.header(CHAT_OFICIAL_NAME)
        st.image(WEBSITE_LOGO, width=150)
        st.markdown(CHAT_DESCRIPTION)
        st.header(f"An Integral part of: [{WEBSITE_NAME}]({WEBSITE_NAME})")
        st.header("Usage Policy")
        st.markdown("- Ask direct and clear questions.")
        st.markdown("- If the response is not correct, rephrase the question.")
        st.markdown("- Wait for the response to make the next question.")
        st.markdown(f"- Troubles? Contact {CONTACT_PERSON}.")        
        
    st.title(CHAT_OFICIAL_NAME)
    st.image(CHAT_LOGO, width=150)
    st.info(CHAT_WELCOME)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "output" in message.keys():
                st.markdown(message["output"])        

    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None

    uploaded_file = st.file_uploader("Upload a file (txt, pdf, html)", type=["txt", "pdf", "html"])    
    
    if prompt := st.chat_input(CHAT_INPUT_MESSAGE):
        
        final_prompt = f"{prompt}\n"
        if uploaded_file and st.session_state.uploaded_file!=uploaded_file.name:
            extracted_text = extract_text_from_file(uploaded_file)

            final_prompt += f"{extracted_text}"
            prompt += f" + whatever is inside this file: {uploaded_file.name}"        
            st.session_state.uploaded_file = uploaded_file.name
        
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "output": prompt})

        data = {"question": final_prompt, "user_id": session_id, "bot": chat_name}

        with st.spinner(CHAT_PROCESSING_MESSAGE):
            response = requests.post(CHATBOT_URL, json=data)

            if response.status_code == 200:
                output_text = response.json()["answer"]
            else:
                output_text = CHAT_ERROR_MESSAGE

        st.chat_message("assistant").markdown(output_text)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "output": output_text,
            }        
        )
else:
    st.title("Bot not found!")
    st.info("Please choose one of the available bots!")