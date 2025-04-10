import streamlit as st
from router import router
from faq import ingest_faq_data,faq_chain
from sql import sql_chain
from small_talk import talk

ingest_faq_data(path = "resources/faq_data.csv")

def ask(query):
    route =  router(query).name
    if route=='faq':
        return faq_chain(query)
    elif route=='sql':
        return sql_chain(query)
    elif route=='small_talk':
        return talk(query)
    else:
        return f"Route {route} not implemented yet"

st.title("E-commerce chatbot")

query = st.chat_input("Write your query")

if "messages" not in st.session_state:
    st.session_state["messages"] = [] 

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



if query:
    with st.chat_message("user"):
        st.markdown(query)


    st.session_state.messages.append(
        {
            "role" : "user",
            "content" : query
        }
    )

    response = ask(query)

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append(
        {
            "role" : "assistant",
            "content" : response
        }
    )