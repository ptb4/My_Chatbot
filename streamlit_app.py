import streamlit as st
from openai import OpenAI
import requests

# Function to fetch supporting articles using a web search
def get_supporting_articles(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key=YOUR_GOOGLE_API_KEY&cx=YOUR_SEARCH_ENGINE_ID"
    response = requests.get(search_url)
    results = response.json().get("items", [])
    return [f"[{item['title']}]({item['link']})" for item in results[:3]]

# Streamlit UI setup
st.title("💬 Debate Chatbot")
st.write(
    "Enter your stance on a topic, and I'll present a counterargument."
)

# Ask for Gemini API Key
gemini_api_key = st.text_input("Gemini API Key", type="password")

if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # Use Gemini API instead of OpenAI
    client = OpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display past chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Ask for user's stance
    stance = st.chat_input("Enter your stance on a topic:")

    if stance:
        # Store and display the user's input
        st.session_state.messages.append({"role": "user", "content": stance})
        with st.chat_message("user"):
            st.markdown(stance)

        # Generate a counterargument using Gemini
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            n=1,
            messages=[
                {"role": "system", "content": "You are a debate assistant. Always provide a well-reasoned counterargument."},
                {"role": "user", "content": f"My stance: {stance}. Provide a counterargument."}
            ]
        )

        # Extract response correctly (fixing the 'ChatCompletionMessage' error)
        counterargument = response.choices[0].message.content  

        # Display the AI's response
        with st.chat_message("assistant"):
            st.markdown(counterargument)

        # Store response in session state
        st.session_state.messages.append({"role": "assistant", "content": counterargument})

        # Find supporting articles
        articles = get_supporting_articles(f"counterargument to {stance}")
        if articles:
            st.write("Here are some supporting articles:")
            for article in articles:
                st.markdown(article)
