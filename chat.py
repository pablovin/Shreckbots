from mechanics_chats.chatbots.chatbots import chat_cmd, get_index, initialize_llm
import argparse
import logging
from dotenv import load_dotenv
import os

CONFIG_DIR = "config_files"
API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")
load_dotenv(API_CONFIG_FILE)

def load_bot_configs():
    bots = {}
    
    for filename in os.listdir(CONFIG_DIR):
        if filename.endswith(".env") and filename != "api.env":
            bot_name = filename.replace(".env", "")
            bots[bot_name] = load_dotenv(os.path.join(CONFIG_DIR, filename))            
    return bots


if __name__ == '__main__':

    parser=argparse.ArgumentParser(description="sample argument parser")
    parser.add_argument("bot")
    args=parser.parse_args()

    bot = args.bot

    bots = load_bot_configs()

    if not bot in bots.keys():
        print (f"Bot Not recognized! Try: {bots.keys()}")
        exit()
    
    initialize_llm(logging)
    
    print (f"Initializing Bot: {bot}")        
    index = get_index(bot, logging)
    
    chat_cmd(index, "Pablo", bot, logging)