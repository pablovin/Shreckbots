from flask import Flask
from waitress import serve
from flask import jsonify
from flask import request, session
from flask_cors import CORS
import logging
import sys
import threading


from mechanics_chats.chatbots.chatbots import initialize_llm, get_index, chat

from mechanics_chats.update_database.update_database import read_wiki_pages, update_embeddings

import argparse

from datetime import timedelta
from dotenv import load_dotenv, dotenv_values
import os

import secrets

secret_key = secrets.token_urlsafe(16)

app = Flask(__name__)
app.secret_key = secret_key
CORS(app)

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG_DIR = "config_files"
def load_bot_configs():
    bots = {}
    app.logger.info('Loading Bots...')
    for filename in os.listdir(CONFIG_DIR):
        if filename.endswith(".env") and filename != "api.env":
            bot_name = filename.replace(".env", "")
            bots[bot_name] = load_dotenv(os.path.join(CONFIG_DIR, filename))
        
    app.logger.info(f' --- Bots Loaded: {bots.keys()}')
    return bots

def get_update_log():

# Set up update logger
    if os.path.exists('update_log.log'):
        os.remove('update_log.log')

    update_logger = logging.getLogger('update_log')
    update_logger.setLevel(logging.INFO)
    update_handler = logging.FileHandler('update_log.log')
    update_logger.addHandler(update_handler)

    return update_logger

def set_loggers():
    # Set up main app logger
    app.logger.setLevel(logging.INFO)
    handler = logging.FileHandler('api.log')
    app.logger.addHandler(handler)
        
    
    return get_update_log()

# Initialize loggers
update_logger = set_loggers()


# REST API

@app.route('/read_wiki', methods=['POST'])
def read_wiki():    
    update_logger = set_loggers()
    json = request.get_json(silent=True)        
    bot = json['bot']

    thread = threading.Thread(target=read_wiki_pages, args=(bot, update_logger))
    # Start the thread
    thread.start()

    # read_wiki_pages(bot, update_logger)    

    data = {'answer':"updated"}
    return jsonify(data), 200

@app.route('/update_embedding', methods=['POST'])
def update_embedding():    
    update_logger = set_loggers()
    json = request.get_json(silent=True)        
    bot = json['bot']
    folder = json['folder']

    thread = threading.Thread(target=update_embeddings, args=(bot, folder, update_logger))    
    thread.start()    

    data = {'answer':"updated"}
    return jsonify(data), 200

@app.route('/chat', methods=['POST'])
def post_question():
    
    json = request.get_json(silent=True)    
    data = get_request(json)
    
    return jsonify(data), 200

def get_request(json):
           
    question = json['question']
    user_id = json['user_id']    
    bot = json['bot']
    # logging.info("post question `%s` for user `%s`", question, user_id)

    print (f"Json: {json}")
    resp = chat(question, index_bots[bot], user_id, bot, app.logger)
    data = {'answer':resp}

    return data



# @app.route('/api/st', methods=['POST'])
# def post_question_st():

#     json = request.get_json(silent=True)
#     data = get_request(index_elder, json, "ELDER")
    
#     return jsonify(data), 200

#     # json = request.get_json(silent=True)

#     # print (f"JSOn: {json}")
#     # question = json['question']
#     # user_id = json['user_id']
    
#     # logging.info("post question `%s` for user `%s`", question, user_id)
        
#     # resp = chat(question, index_elder, user_id, "ELDER")
#     # data = {'answer':resp}

#     # return jsonify(data), 200


# @app.route('/api/dm', methods=['POST'])
# def post_question_dm():
    
#     json = request.get_json(silent=True)
#     data = get_request(index_sage, json, "SAGE")
    
#     return jsonify(data), 200


#     # json = request.get_json(silent=True)

#     # print (f"JSOn: {json}")
#     # question = json['question']
#     # user_id = json['user_id']    
#     # logging.info("post question `%s` for user `%s`", question, user_id)

#     # resp = chat(question, index_sage, user_id, "SAGE")
#     # data = {'answer':resp}

#     # return jsonify(data), 200

# @app.route('/api/mt', methods=['POST'])
# def post_question_mt():
    
#     json = request.get_json(silent=True)

#     data = get_request(index_mestre, json, "MESTRE")
    
#     return jsonify(data), 200





def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)
    session.modified = True
    session["chat_id"] = session["chat_id"]


# API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")



# config = {
#     **dotenv_values(API_CONFIG_FILE),  # load shared development variables
#     # **dotenv_values(".env.secret"),  # load sensitive variables
#     **os.environ,  # override loaded values with environment variables
# }

if __name__ == '__main__':
    
    app.logger.info('-------------------------')
    app.logger.info('Starting the Server')
    app.logger.info('-------------------------')

    parser = argparse.ArgumentParser(description="Run the chatbot script.")
    parser.add_argument("no_bots", nargs='?', default=None, help="Not initializing the chatbots (optional)")
    args = parser.parse_args()

    no_bots = args.no_bots
            
    #Initialize LLM
    try:

        # #Load all the available bots
        bots = load_bot_configs()
        if not no_bots:
            initialize_llm(app.logger)        
            index_bots = {}
            for bot in bots.keys():
                index_bots[bot] = get_index(bot, app.logger)
                app.logger.info(f"SERVING {bot}")
            
    except Exception  as e:
        app.logger.error(f"ERROR: {e.with_traceback()}")

    serve(app, host=os.getenv("API_HOST"), port=int(os.getenv("API_PORT")))

