import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from cryptography.fernet import Fernet
import yagmail


# --------------------------
# Load Secrets
# --------------------------
MONGO_URI = st.secrets["MONGO_URI"]
ENC_KEY = st.secrets["ENCRYPTION_KEY"]

EMAIL_USER = st.secrets["EMAIL_USER"]      # your Gmail
EMAIL_PASS = st.secrets["EMAIL_PASS"]      # gmail app password

fernet = Fernet(ENC_KEY)

# --------------------------
# MongoDB Setup
# --------------------------
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client["twitter_vault"]
collection = db["accounts"]


# --------------------------
# Send Email Function
# --------------------------
def send_notification(email_to, username):
    try:
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)
        yag.send(
            to=email_to,
            subject="Twitter Credentials Updated",
            contents=f"""
Your Twitter developer credentials were securely updated.

Twitter Username: {username}

If this wasn't you, please update your credentials immediately.
            """
        )
        return True
    except Exception as e:
        st.error(f"Email Failed: {e}")
        return False


# --------------------------
# UI Layout
# --------------------------
st.title("🔐 Secure Twitter Developer Credential Vault")
st.caption("Safely store API Key, API Secret, Email, and Username — fully encrypted.")

# Input fields (masked)
api_key = st.text_input("API Key", type="password")
api_secret = st.text_input("API Secret", type="password")
email_id = st.text_input("Email ID for Notifications")
twitter_username = st.text_input("Twitter Username", placeholder="@username")


# --------------------------
# Save Handler
# --------------------------
if st.button("Save Securely"):
    if not api_key or not api_secret or not email_id or not twitter_username:
        st.warning("All fields are required.")
    else:
        encrypted_entry = {
            "api_key": fernet.encrypt(api_key.encode()).decode(),
            "api_secret": fernet.encrypt(api_secret.encode()).decode(),
            "email_id": fernet.encrypt(email_id.encode()).decode(),
            "twitter_username": fernet.encrypt(twitter_username.encode()).decode(),
        }

        collection.insert_one(encrypted_entry)
        st.success("🔥 Credentials encrypted & stored safely in MongoDB.")

        # Send notification
        if send_notification(email_id, twitter_username):
            st.success("📩 Notification email sent successfully!")
