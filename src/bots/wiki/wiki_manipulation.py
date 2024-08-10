import os
import requests
from requests.exceptions import HTTPError
import getpass
from dotenv import load_dotenv
import logging
from mediawiki import MediaWiki
import shutil 


CONFIG_DIR = "config_files"

def load_shreckbot_config():
    
    API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")
    load_dotenv(API_CONFIG_FILE)
    
def load_bot_config(bot):
    
    config_file_bot = os.path.join(CONFIG_DIR, f"{bot}.env")
    load_dotenv(config_file_bot)  


def get_login_token(mediawiki, logger):
    params={
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }

    login_token = mediawiki.wiki_request(params=params)['query']['tokens']['logintoken']

    # logger.warning(f" --- Login token: {login_token}")

def login_wiki(mediawiki,login_token,username, password, logger):
     
     result_login = mediawiki.login(username, password)
    #  params={
    #         "action": "login",
    #         "lgname": username,
    #         "lgpassword": password,
    #         "lgtoken": login_token,
    #         "format": "json"
    #     }
    #  result_login = mediawiki.wiki_request(params=params)
    #  logger.warning(f" --- Login result: {result_login}")   

     return result_login

def get_CRFS_Token(mediawiki, logger):
    params={
        "action": "query",
        "meta": "tokens",
        "format": "json"         
        }
    crfs_token = mediawiki._post_response(params=params)['query']['tokens']['csrftoken']
    # logger.warning(f" --- CRFS Token result: {crfs_token}")  
    return crfs_token

def upload_page(mediawiki, csrf_token, page_name, page_content, logger):

    params={
            "action": "edit",
            "title": page_name,
            "text": page_content,
            "token": csrf_token,
            "format": "json",
            "summary": "Page created/updated automatically using script."
        }
        
    result_upload = mediawiki._post_response(params=params)["edit"]["result"]

    return result_upload
   

def upload_pages(bot, pages, logger):
    load_shreckbot_config()
    load_bot_config(bot)

    wiki_url = os.getenv(f"WIKI_API_URL_{bot}")
    folder_path = os.path.join(os.getenv("WIKI_PAGES_FOLDER"),bot)
    username = os.getenv(f"WIKI_USERNAME_{bot}")
    password = os.getenv(f"WIKI_PASSWORD_{bot}")

    mediawiki = MediaWiki(url=wiki_url)

    logger.warning(f"Uploading pages to: {bot}")        
    logger.warning(f" -- Wiki: {wiki_url}")        
    logger.warning(f" -- Pages: {pages}")            

    logger.warning(f" -- Getting login token...")        
    login_token = get_login_token(mediawiki,logger)

    logger.warning(f" -- Loging in...")        
    login_result = login_wiki(mediawiki,login_token,username, password, logger)

    if login_result:
        logger.warning(f" -- Getting CSFR Token ...")     
        csrf_token = get_CRFS_Token(mediawiki, logger)

        logger.warning(f" -- Creating pages ...")     
        for page in pages:
            logger.warning(f" ---- Page {page} ...")  
            file_name = os.path.join(folder_path,page+".txt")            
            with open(file_name, 'r') as file:
                page_content = file.read()
                result = upload_page(mediawiki, csrf_token, page, page_content, logger)
                logger.warning(f" ------- Result: {result}")  
                if result:
                    os.remove(file_name)




def main():

    bot = "Elder"    
    pages = ["Agonos"]    
    # print (f"text_input: {text_input}")
    upload_pages(bot, pages, logging)

if __name__ == "__main__":
    main() 



# # Configuration
# wiki_url = "https://your-wiki-url.com"  # Replace with your MediaWiki URL
# api_endpoint = f"{wiki_url}/api.php"
# folder_path = "path/to/your/folder"  # Replace with your folder path
# file_name = "yourfile.txt"  # Replace with your file name

# # User authentication
# username = input("Enter your wiki username: ")
# password = getpass.getpass("Enter your wiki password: ")

# # Create a session
# session = requests.Session()

# # Step 1: Get login token
# try:
#     response = session.get(api_endpoint, params={
#         "action": "query",
#         "meta": "tokens",
#         "type": "login",
#         "format": "json"
#     })
#     response.raise_for_status()
#     login_token = response.json()['query']['tokens']['logintoken']
# except HTTPError as e:
#     print(f"Failed to get login token: {e}")
#     exit()

# # Step 2: Log in
# try:
#     response = session.post(api_endpoint, data={
#         "action": "login",
#         "lgname": username,
#         "lgpassword": password,
#         "lgtoken": login_token,
#         "format": "json"
#     })
#     response.raise_for_status()
#     if response.json()['login']['result'] != "Success":
#         print("Login failed!")
#         exit()
# except HTTPError as e:
#     print(f"Login request failed: {e}")
#     exit()

# print("Login successful!")

# # Step 3: Get a CSRF token (needed to edit pages)
# try:
#     response = session.get(api_endpoint, params={
#         "action": "query",
#         "meta": "tokens",
#         "format": "json"
#     })
#     response.raise_for_status()
#     csrf_token = response.json()['query']['tokens']['csrftoken']
# except HTTPError as e:
#     print(f"Failed to get CSRF token: {e}")
#     exit()

# # Read file content
# file_path = os.path.join(folder_path, file_name)
# with open(file_path, 'r') as file:
#     page_content = file.read()

# # Get page name (file name without extension)
# page_name = os.path.splitext(file_name)[0]

# # Step 4: Create or edit the wiki page
# try:
#     response = session.post(api_endpoint, data={
#         "action": "edit",
#         "title": page_name,
#         "text": page_content,
#         "token": csrf_token,
#         "format": "json",
#         "summary": "Page created/updated automatically using script."
#     })
#     response.raise_for_status()
#     result = response.json()
#     if result.get("edit", {}).get("result") == "Success":
#         print(f"Page '{page_name}' created/updated successfully!")
#     else:
#         print(f"Failed to create/update page '{page_name}'. Response: {result}")
# except HTTPError as e:
#     print(f"Failed to edit page: {e}")
# finally:
#     # Step 5: Logout
#     session.post(api_endpoint, data={
#         "action": "logout",
#         "format": "json"
#     })
#     print("Logged out successfully.")