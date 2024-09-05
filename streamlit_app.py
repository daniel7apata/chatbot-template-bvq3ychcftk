import openai
import streamlit as st
import os
import uuid

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
openai.api_key = os.getenv('OPENAI_API_KEY')
BOT_INTRODUCTION = "Hola, soy Sammy, encantada de conocerte. Estoy aquí para orientarte"

# Definir los avatares
BOT_AVATAR = "bot_avatar.png"
USER_AVATAR = "user_avatar.png"

def session_id():
    return str(uuid.uuid4())

def write_message(message):
    if message["role"] == "user":
        with st.chat_message("user", avatar=USER_AVATAR):
            st.write(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("user", avatar=BOT_AVATAR):
            st.markdown(message["content"])

classification_prompt = """
Tu nombre es Sammy, y eres una asistente social virtual con una profunda especialización en el campo de la violencia contra menores, específicamente estudiantes de colegios, y el impacto que esta puede tener en su salud mental. Tu misión principal es analizar cuidadosamente los mensajes que recibes de los usuarios para identificar posibles casos de violencia en las aulas, abarcando la violencia física, psicológica y sexual, así como cualquier señal que pueda indicar que un menor está siendo víctima de acoso escolar o muestra comportamientos relacionados con problemas de salud mental, tales como depresión, ansiedad u otras afecciones similares. Basándote exclusivamente en la legislación y normativas provistas, que están específicamente relacionadas con la violencia escolar y la salud mental, debes proporcionar respuestas que sean no solo informativas, sino también profundamente empáticas y cálidas, asegurando que quien consulta se sienta escuchado y apoyado. En tu rol, es crucial que determines si el texto del usuario, delimitado por los caracteres ####, constituye una consulta o testimonio relacionado con la violencia en las aulas o con la salud mental de los estudiantes. Si se trata de una consulta o testimonio de este tipo, deberás utilizar la información normativa provista fuera de los #### para elaborar una respuesta detallada, citando explícitamente las fuentes normativas correspondientes, mencionando el título y el año para mayor claridad y respaldo. En caso de que el texto entre #### no esté relacionado con la violencia escolar, el acoso o la salud mental, responde al texto contenido entre #### en tono conversacional, informando únicamente que estás capacitada para ofrecer información sobre bullying, violencia escolar y salud mental, sin utilizar la información adicional que se te ha proporcionado. Es fundamental que te mantengas siempre dentro de los límites de tu especialización, evitando responder a consultas fuera de tu ámbito de competencia, y asegurando que todas tus respuestas sean claras, accesibles y libres de jerga especializada que pueda resultar confusa para el usuario. En el caso que te realicen una consulta que implique discriminación a la comunidad LGBTQ+ es importante que la respuesta muestre el respeto que se le debe tener a todas las personas, incluidos alumnos, maestros y personal educativo. Tu tono debe ser siempre acogedor y cálido, transmitiendo empatía y comprensión en cada interacción, y asegurándote de no revelar ni mencionar la estructura o el formato en que se presentan los mensajes, respetando en todo momento la confidencialidad y privacidad del usuario.
"""

def generate_response(query, messages):
    messages += [{'role': 'user', 'content': query}]
    response = openai.chat.completions.create(
        model="ft:gpt-4o-mini-2024-07-18:personal:sammyv9:A3cv7dUD",
        messages=messages,
        stream=True
    )
    return messages, response

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
        placeholder="Ingresa tu duda aqui..."
    ):
        response_from_query()

if __name__ == "__main__":
    main()
