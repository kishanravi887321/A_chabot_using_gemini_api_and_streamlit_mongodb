import streamlit as st
import google.generativeai as genai
from pymongo import MongoClient
from datetime import datetime

# Configure the API key
genai.configure(api_key="AIzaSyAsdfszXAZhxm9mBu1wIsdfdTxbdZ9bfwXRSqxKdsfJzE--replaced api key")  # Replace with your API key

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017')  # Adjust if using a remote MongoDB server
db = client['chatbot_db']  # Use a database for your chatbot
collection = db['chat_history']  # Use a collection to store chat history

# Set up Streamlit UI
st.set_page_config(layout="wide")  # Set wide layout for better space usage

# Title and Subheader
st.title("Generative AI Chatbot")
st.markdown("""### Powered by Gemini API and Streamlit""")

# Initialize session state for user input and bot response
if "bot_response" not in st.session_state:
    st.session_state.bot_response = None

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Function to get the Gemini model response
def get_gimini_response(question):
    model = genai.GenerativeModel('gemini-pro')
    res = model.generate_content(question)
    return res.text


# Function to load chat history from MongoDB
def load_chat_history():
    history = []
    for chat in collection.find():
        history.append(chat)
    history.sort(key=lambda x: x['timestamp'], reverse=True)  # Sort by timestamp (newest first)
    return history


# Function to save chat history to MongoDB
def save_chat_history(user_message, bot_message):
    timestamp = datetime.now()
    collection.insert_one({
        'user_message': user_message,
        'bot_message': bot_message,
        'timestamp': timestamp
    })


# Initialize chat history by loading from MongoDB
history = load_chat_history()

# Layout: Two columns for user and bot message side by side
col1, col2 = st.columns([2, 3])

# Left column: Chat History
with col1:
    st.subheader("Chat History")
    # Display chat history with expandable text for detailed view
    for chat in history:
        if 'user_message' in chat and 'bot_message' in chat:
            # New schema: Show combined user and bot messages with preview
            preview = f"**You:** {chat['user_message'][:50]}... | **Bot:** {chat['bot_message'][:50]}..."
            with st.expander(preview):
                st.markdown(f"**You:** {chat['user_message']}\n\n**Bot:** {chat['bot_message']}")
        else:
            # Old schema: Display individual messages
            preview = f"**{chat['role'].capitalize()}:** {chat['message'][:50]}..."
            with st.expander(preview):
                st.markdown(f"**{chat['role'].capitalize()}:** {chat['message']}")
        st.markdown("---")

# Right column: User input and response display
with col2:
    # User input area
    st.session_state.user_input = st.text_input("You:", placeholder="Type your message here...")

    if st.button("Send") and st.session_state.user_input:
        with st.spinner("Generating response..."):
            # Generate the bot response
            st.session_state.bot_response = get_gimini_response(st.session_state.user_input)

        # Display the bot response immediately
        st.text_area("Bot Response:", value=st.session_state.bot_response, height=min(200 + len(st.session_state.bot_response) // 100, 400), disabled=True)

        # Save the conversation to MongoDB
        save_chat_history(st.session_state.user_input, st.session_state.bot_response)

        # Clear the input field
        st.session_state.user_input = ""

# Optional: Display the last bot response if exists
if st.session_state.bot_response:
    st.text_area("Last Bot Response:", value=st.session_state.bot_response, height=min(200 + len(st.session_state.bot_response) // 100, 400), disabled=True)
