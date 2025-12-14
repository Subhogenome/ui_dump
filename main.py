import streamlit as st
from pymongo import MongoClient
from cryptography.fernet import Fernet

# Load secrets from Streamlit
MONGO_URI = st.secrets["MONGO_URI"]
ENCRYPTION_KEY = st.secrets["ENCRYPTION_KEY"]

# Setup encryption
fernet = Fernet(ENCRYPTION_KEY)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["secure_storage"]
collection = db["credentials"]

st.title("🔐 Secure API & Token Dump UI (Encrypted → MongoDB Atlas)")

st.subheader("Enter Sensitive Information")
api_key = st.text_input("API Key", type="password")
auth_token = st.text_input("Auth Token", type="password")
email_id = st.text_input("Email ID")

if st.button("Save Securely"):
    if not api_key and not auth_token and not email_id:
        st.warning("Provide at least one field.")
    else:
        encrypted_data = {
            "api_key": fernet.encrypt(api_key.encode()).decode() if api_key else None,
            "auth_token": fernet.encrypt(auth_token.encode()).decode() if auth_token else None,
            "email_id": fernet.encrypt(email_id.encode()).decode() if email_id else None,
        }

        collection.insert_one(encrypted_data)
        st.success("🔥 Data encrypted & securely saved to MongoDB Atlas!")

st.markdown("---")

st.subheader("🔍 Decrypt (Admin Only)")
admin_input = st.text_input("Enter encrypted string to decrypt", type="password")

if st.button("Decrypt"):
    try:
        decrypted_value = fernet.decrypt(admin_input.encode()).decode()
        st.success(f"Decrypted value: {decrypted_value}")
    except Exception:
        st.error("Invalid encrypted text or key.")
