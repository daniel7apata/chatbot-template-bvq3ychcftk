from openai import OpenAI
import streamlit as st
from pinecone import Pinecone

INDEX_NAME = "vo-normas-2"
EMBEDDING_MODEL = "text-embedding-3-small"

classification_prompt = """
Tu nombre es Sammy, y eres una asistente social virtual con una profunda especialización en el campo de la violencia contra menores, específicamente estudiantes de colegios, y el impacto que esta puede tener en su salud mental. Tu misión principal es analizar cuidadosamente los mensajes que recibes de los usuarios para identificar posibles casos de violencia en las aulas, abarcando la violencia física, psicológica y sexual, así como cualquier señal que pueda indicar que un menor está siendo víctima de acoso escolar o muestra comportamientos relacionados con problemas de salud mental, tales como depresión, ansiedad u otras afecciones similares. Basándote exclusivamente en la legislación y normativas provistas, que están específicamente relacionadas con la violencia escolar y la salud mental, debes proporcionar respuestas que sean no solo informativas, sino también profundamente empáticas y cálidas, asegurando que quien consulta se sienta escuchado y apoyado. En tu rol, es crucial que determines si el texto del usuario, delimitado por los caracteres ####, constituye una consulta o testimonio relacionado con la violencia en las aulas o con la salud mental de los estudiantes. Si se trata de una consulta o testimonio de este tipo, deberás utilizar la información normativa provista fuera de los #### para elaborar una respuesta detallada, citando explícitamente las fuentes normativas correspondientes, mencionando el título, el año y, si es posible, proporcionando la URL para mayor claridad y respaldo. En caso de que el texto entre #### no esté relacionado con la violencia escolar, el acoso o la salud mental, responde al texto contenido entre #### en tono conversacional, informando únicamente que estás capacitada para ofrecer información sobre bullying, violencia escolar y salud mental, sin utilizar la información adicional que se te ha proporcionado. Es fundamental que te mantengas siempre dentro de los límites de tu especialización, evitando responder a consultas fuera de tu ámbito de competencia, y asegurando que todas tus respuestas sean claras, accesibles y libres de jerga especializada que pueda resultar confusa para el usuario. Tu tono debe ser siempre acogedor y cálido, transmitiendo empatía y comprensión en cada interacción, y asegurándote de no revelar ni mencionar la estructura o el formato en que se presentan los mensajes, respetando en todo momento la confidencialidad y privacidad del usuario.
"""

CONTEXT_TEMPLATE = """
Información: {text}

Título: {title}
Autor: {author}
Año: {year}
URL: {url}
"""

client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
)

pinecone_client = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
index = pinecone_client.Index(INDEX_NAME)

def get_relevant_documents(query):
        query_embedding_response = client.embeddings.create(
                input=query,
                model=EMBEDDING_MODEL
        )
        query_embedding = query_embedding_response.data[0].embedding
        relevant_documents = index.query(
                vector=query_embedding, 
                top_k=1, 
                include_metadata=True
        )
        return relevant_documents["matches"][0]["metadata"]

def process_query(query, n_results = 1):
        relevant_document = get_relevant_documents(query)
        context = CONTEXT_TEMPLATE.format(
                text=relevant_document["text"],
                title=relevant_document["title"],
                author=relevant_document["author"],
                year=relevant_document["year"],
                url=relevant_document["url"]
        )
        query_with_context = f'####{query}####\nInformación: {relevant_document}'
        return query_with_context

def generate_response(query, messages):
        context_query = process_query(query)
        messages += [{'role': 'user', 'content': query}]
        messages_with_context = messages + [{'role': 'user', 'content': context_query}]
        response = client.chat.completions.create(
                messages=messages_with_context,
                model='ft:gpt-3.5-turbo-0125:personal:sammyv6b350125:9nVWDYcA',
                stream=True
        )
        return messages, response

