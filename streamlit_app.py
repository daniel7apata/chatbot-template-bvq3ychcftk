import streamlit as st


from openai import OpenAI

import openai
import streamlit as st
import os
from html_template import *
from generate_response import classification_prompt, generate_response
from supabase import create_client, Client
import uuid
import time
from env_type import production

# Show title and description.
#st.title("Sammy")
st.write(
    "Hola, soy Sammy. Es un placer conocerte ¿en qué puedo ayudarte?"
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management

#openai_api_key = st.text_input("OpenAI API Key", type="password")
openai_api_key = st.secrets ["OPENAI_API_KEY"]

DATABASE_NAME = "vog-chatbot"
BOT_INTRODUCTION = "Hola, soy Sammy. Es un placer conocerte ¿en qué puedo ayudarte?"

if production:
    supabase: Client = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
    )

def insert_data(uuid, message, table = DATABASE_NAME):
    data = {"uuid": uuid, "role": message["role"], "content": message["content"]}
    row_insert = supabase.table(table).insert(data)
    return row_insert

def session_id():
    return str(uuid.uuid4())

def write_message(message):
    if message["role"] == "user":
        with st.chat_message("user", avatar=USER_AVATAR):
            st.write(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("user", avatar=BOT_AVATAR):
            st.markdown(message["content"])

def response_from_query():
    if st.session_state.prompt == "":
        return

    for message in st.session_state.history:
        write_message(message)

    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(st.session_state.prompt)
    messages = st.session_state.history

    messages, response = generate_response(st.session_state.prompt, messages)
    st.session_state.history = messages

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        assistant_message = st.write_stream(response)
    
    st.session_state.history.append(
        {"role": "assistant", "content": assistant_message}
    )
    messages = st.session_state.history
    if production:
        insert_data(st.session_state.session_id, messages[-2]).execute()
        insert_data(st.session_state.session_id, messages[-1]).execute()

def main():

    if "session_id" not in st.session_state:
        st.session_state.session_id = session_id()
        
    if "history" not in st.session_state:
        st.session_state.history = [{'role': 'system', 'content': classification_prompt}]

    if "stream" not in st.session_state:
        st.session_state.stream = None
    
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        st.write(BOT_INTRODUCTION)
    
    if prompt := st.chat_input(
        key="prompt", 
        placeholder="Ingresa tu duda aquí..."
    ):
        response_from_query()

if __name__ == "__main__":
    main()
