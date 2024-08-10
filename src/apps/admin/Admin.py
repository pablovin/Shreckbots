import streamlit as st

st.set_page_config(
    page_title="Admin_App",
    page_icon="👋",
)

st.write("# Welcome to Shreckbots Admin page! 👋")

st.sidebar.success("Select one of the tools above.")

st.markdown(
    """
    Shreckbots is a tool for using and deploying LLM-powered chatbots, integrated with a MediaWiki.\n
    The Admin page helps you to manage your bots and automatize the wiki generation.
    **👈 Select a tool from the sidebar** and see what you can do with Shreckbots!
    ### Want to learn more?
    - Check out [Shreckbots Github Page](https://github.com/pablovin/Shreckbots)    
"""
)