import streamlit as st
from utils_admin import load_api_config, save_api_config


st.set_page_config(page_title="Shreckbot Configurations", page_icon="📈")
st.title("ShreckBots – API Configurations")

api_config = load_api_config()

if not api_config:
    st.write("No API configurations found.")
 
else:
    st.subheader("Edit API Configurations")
    st.markdown("---")
    st.write("Use this page to update all the important global configurations for Shreckbots.")
    st.write("Check the meaning of each of these parameters in our Shreckbot manual: https://github.com/pablovin/Shreckbots")
    st.markdown("---")
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
            st.success("API config updated successfully.")
        else:
            st.error("All fields must be filled.")
