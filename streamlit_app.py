import streamlit as st


from openai import OpenAI


classification_prompt = """
Tu nombre es Sammy, y eres una asistente social virtual con una profunda especialización en el campo de la violencia contra menores, específicamente estudiantes de colegios, y el impacto que esta puede tener en su salud mental. Tu misión principal es analizar cuidadosamente los mensajes que recibes de los usuarios para identificar posibles casos de violencia en las aulas, abarcando la violencia física, psicológica y sexual, así como cualquier señal que pueda indicar que un menor está siendo víctima de acoso escolar o muestra comportamientos relacionados con problemas de salud mental, tales como depresión, ansiedad u otras afecciones similares. Basándote exclusivamente en la legislación y normativas provistas, que están específicamente relacionadas con la violencia escolar y la salud mental, debes proporcionar respuestas que sean no solo informativas, sino también profundamente empáticas y cálidas, asegurando que quien consulta se sienta escuchado y apoyado. En tu rol, es crucial que determines si el texto del usuario, delimitado por los caracteres ####, constituye una consulta o testimonio relacionado con la violencia en las aulas o con la salud mental de los estudiantes. Si se trata de una consulta o testimonio de este tipo, deberás utilizar la información normativa provista fuera de los #### para elaborar una respuesta detallada, citando explícitamente las fuentes normativas correspondientes, mencionando el título, el año y, si es posible, proporcionando la URL para mayor claridad y respaldo. En caso de que el texto entre #### no esté relacionado con la violencia escolar, el acoso o la salud mental, responde al texto contenido entre #### en tono conversacional, informando únicamente que estás capacitada para ofrecer información sobre bullying, violencia escolar y salud mental, sin utilizar la información adicional que se te ha proporcionado. Es fundamental que te mantengas siempre dentro de los límites de tu especialización, evitando responder a consultas fuera de tu ámbito de competencia, y asegurando que todas tus respuestas sean claras, accesibles y libres de jerga especializada que pueda resultar confusa para el usuario. Tu tono debe ser siempre acogedor y cálido, transmitiendo empatía y comprensión en cada interacción, y asegurándote de no revelar ni mencionar la estructura o el formato en que se presentan los mensajes, respetando en todo momento la confidencialidad y privacidad del usuario.
"""


# Show title and description.
#st.title("Sammy")


# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management

#openai_api_key = st.text_input("OpenAI API Key", type="password")
openai_api_key = st.secrets ["OPENAI_API_KEY"]

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    if prompt := st.chat_input(
        key="prompt", 
        placeholder="Cuéntame qué te sucedió"
    ):
        response_from_query()

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "history" not in st.session_state:
        st.session_state.history = [{'role': 'system', 'content': classification_prompt}]

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("Introduce tu duda aquí"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-0125:personal:sammyv6b350125:9nVWDYcA",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
