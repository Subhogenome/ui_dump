import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Load from Streamlit Secrets
uri = st.secrets["MONGO_URI"]

# Create MongoDB client
client = MongoClient(uri, server_api=ServerApi('1'))

# Test connection
try:
    client.admin.command("ping")
    st.success("Ping successful! Connected to MongoDB Atlas.")
except Exception as e:
    st.error(f"Connection failed: {e}")
