import os
import streamlit as st
import requests
import time
from dotenv import load_dotenv, dotenv_values

# Load environment variables
CONFIG_DIR = "config_files"
API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")
load_dotenv(API_CONFIG_FILE)

def load_bot_configs():
    bots = {}
    for filename in os.listdir(CONFIG_DIR):
        if filename.endswith(".env") and filename != "api.env":
            bot_name = filename.replace(".env", "")
            bots[bot_name] = dotenv_values(os.path.join(CONFIG_DIR, filename))
    return bots

def get_files_in_wiki_folder(folder_path):
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

def read_log_contents(log_file_path):
    """Reads the contents of the log file."""
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as file:
            return file.read()
    return ""

st.set_page_config(page_title="Update Wiki Pages", page_icon="📈")

st.title("ShreckBots – Update Wiki Pages")

st.markdown("---")
st.write("""This page allows you to update the wiki based on the content I suggested.
            I will only be able to upload content if you already asked me to generate content using the Create Wiki Pages tool.
         """)
st.write("First, select the bot you want to create pages to using the side bar.")
st.write("Second, update any of the sugested content you want me to update. You can do this by clicking on the content name and editing the content.")
st.write("Third, select the content you want me to upload to the wiki.")
st.write("I will tell you which pages will be updated and which pages will be created.")
st.write("Need more information? Check our Shreckbot manual: https://github.com/pablovin/Shreckbots")

st.markdown("---")

# Load bot configurations
bots = load_bot_configs()
bot_names = list(bots.keys())

if not bot_names:
    st.sidebar.write("No chat bots available.")
else:
    # Sidebar: Select bot
    selected_bot_name = st.sidebar.selectbox("Select a bot", bot_names)
    if selected_bot_name:
        wiki_files_new_directory = os.path.join(os.getenv('WIKI_PAGES_FOLDER'), selected_bot_name,"NewPage")
        wiki_files_update_directory = os.path.join(os.getenv('WIKI_PAGES_FOLDER'), selected_bot_name,"UpdatePage")
        
        wiki_files_new = []
        wiki_files_update = []
        
        if os.path.exists(wiki_files_new_directory):
            wiki_files_new = get_files_in_wiki_folder(wiki_files_new_directory)
        if os.path.exists(wiki_files_update_directory):                 
            wiki_files_update = get_files_in_wiki_folder(wiki_files_update_directory)

        
        
        # print (wiki_files_new)
        # print (wiki_files_update)
        if (len(wiki_files_new)==0 and len(wiki_files_update)==0) :
            st.warning("No pages to be uploaded! Create new pages first!")
        else:
            st.write("## Uploading Wiki Pages")
            include_files_update = {}
        
            col1, col2, col3= st.columns(3)
            with col1:
                st.subheader("Page")
            with col2:
                st.subheader("Type")            
            with col3:
                st.subheader("Upload")            
                
            for file_name in wiki_files_update:
                page_name = os.path.splitext(file_name)[0]
                col1, col2, col3= st.columns(3)
                with col1:                    
                    if st.button(page_name):
                        if 'editing_page' in st.session_state and st.session_state['editing_page'] == page_name:
                            del st.session_state['editing_page']
                            del st.session_state['file_content']
                        else:
                            st.session_state['editing_page'] = page_name
                            # Load the file content when the button is clicked
                            with open(os.path.join(wiki_files_update_directory, file_name), 'r') as file:
                                st.session_state['file_content'] = file.read()

                if 'editing_page' in st.session_state and st.session_state['editing_page'] == page_name:
                    edited_content = st.text_area(f"Edit {page_name}", value=st.session_state.get('file_content', ''), height=300)
                    st.markdown("---")
                    # Save the edited content
                    save_button = st.button(f"Save {page_name}")
                    st.markdown("---")
                    if save_button:
                        with open(os.path.join(wiki_files_update_directory, file_name), 'w') as file:
                            file.write(edited_content)
                        st.success(f"Page '{page_name}' saved successfully.")
                        del st.session_state['editing_page']
                        del st.session_state['file_content']

                with col2:                    
                    st.text("Update Page")

                with col3:
                    # Add checkbox to include the file for upload
                    include_files_update[page_name] = st.checkbox(f"Include", key=file_name, value=False)

            include_files_New = {}
                                   
            for file_name in wiki_files_new:
                page_name = os.path.splitext(file_name)[0]
                col1, col2, col3= st.columns(3)
                with col1:                    
                    if st.button(page_name):
                        if 'editing_page' in st.session_state and st.session_state['editing_page'] == page_name:
                            del st.session_state['editing_page']
                            del st.session_state['file_content']
                        else:
                            st.session_state['editing_page'] = page_name
                            # Load the file content when the button is clicked
                            with open(os.path.join(wiki_files_new_directory, file_name), 'r') as file:
                                st.session_state['file_content'] = file.read()

                if 'editing_page' in st.session_state and st.session_state['editing_page'] == page_name:
                    edited_content = st.text_area(f"Edit {page_name}", value=st.session_state.get('file_content', ''), height=300)
                    st.markdown("---")
                    # Save the edited content
                    save_button = st.button(f"Save {page_name}")
                    st.markdown("---")
                    if save_button:
                        with open(os.path.join(wiki_files_new_directory, file_name), 'w') as file:
                            file.write(edited_content)
                        st.success(f"Page '{page_name}' saved successfully.")
                        del st.session_state['editing_page']
                        del st.session_state['file_content']

                with col2:                    
                    st.text("Create Page")

                with col3:
                    # Add checkbox to include the file for upload
                    include_files_New[page_name] = st.checkbox(f"Include", key=file_name, value=False)


            # Upload selected files to the wiki
            st.markdown("---")
            if st.button("Upload to Wiki"):
                selected_files_new = [name for name, include in include_files_New.items() if include]
                selected_files_update = [name for name, include in include_files_update.items() if include]
                
                if selected_files_new or selected_files_update:

                    # Perform the upload
                    response = requests.post(
                        f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/upload_wiki_pages",
                        json={"bot": selected_bot_name, "new_pages": selected_files_new, "update_pages":selected_files_update}
                    )
                    
                    if response.status_code == 200:
                        st.success("Starting page upload...")
                        
                        # Start reading the log file
                        log_file_path = 'update_log.log'
                        log_contents = st.empty()
                        stop_logging = False

                        while not stop_logging:
                            content = read_log_contents(log_file_path)
                            log_contents.text(content)
                            if " --- Update Done!" in content:
                                stop_logging = True
                            time.sleep(1)
                    else:
                        st.error("Failed to upload pages.")
                else:
                    st.warning("No files selected for upload.")