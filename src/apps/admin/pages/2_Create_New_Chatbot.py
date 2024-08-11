import os
import streamlit as st
from dotenv import dotenv_values
from utils_admin import load_needed_fields, save_bot_config, load_bot_configs

st.set_page_config(page_title="New Chatbots", page_icon="📈")

st.title("ShreckBots – Create New Chat Bot")

needed_fields = load_needed_fields()
bots = load_bot_configs()
bot_names = list(bots.keys())

st.subheader("Create a New Chat Bot")
st.markdown("---")
st.write("Type the new chatbot name, and fill all the important parameters to create a new chatbot!")
st.markdown("---")
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
        
        if st.button("Create Bot") and all_filled:
            save_bot_config(new_bot_name, new_bot_config)
            st.success(f"Bot '{new_bot_name}' created successfully!")
            st.rerun()  # Reset the form after creation