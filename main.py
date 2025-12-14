import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from cryptography.fernet import Fernet
import smtplib
from email.mime.text import MIMEText


# --------------------------
# Load Secrets
# --------------------------
MONGO_URI = st.secrets["MONGO_URI"]
ENC_KEY = st.secrets["ENCRYPTION_KEY"]
EMAIL_USER = st.secrets["EMAIL_USER"]
EMAIL_PASS = st.secrets["EMAIL_PASS"]

fernet = Fernet(ENC_KEY)

# --------------------------
# MongoDB Setup
# --------------------------
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client["twitter_vault"]
collection = db["accounts"]


# --------------------------
# Function to Send Email
# --------------------------
def send_notification(email):
    msg = MIMEText("Your Twitter developer credentials have been updated securely.")
    msg["Subject"] = "Twitter Credentials Updated"
    msg["From"] = EMAIL_USER
    msg["To"] = email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, [email], msg.as_string())
        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False


# --------------------------
# UI
# --------------------------
st.title("🔐 Twitter Credentials Secure Store")
st.caption("Stores API Key, API Secret & Email in encrypted form. Sends update email automatically.")

# Account selection
account = st.selectbox("Select Account", ["Account 1", "Account 2", "Account 3", "Account 4", "Account 5", "Custom"])

if account == "Custom":
    account = st.text_input("Enter Custom Account Name")

st.subheader("Enter Credentials")

email = st.text_input("Email ID (for update notification)")
api_key = st.text_input("API Key", type="password")
api_secret = st.text_input("API Secret", type="password")

if st.button("Save"):
    if not email:
        st.warning("Email is required.")
    else:
        encrypted = {
            "account": account,
            "email": fernet.encrypt(email.encode()).decode(),
            "api_key": fernet.encrypt(api_key.encode()).decode() if api_key else None,
            "api_secret": fernet.encrypt(api_secret.encode()).decode() if api_secret else None,
        }

        collection.insert_one(encrypted)
        st.success(f"Saved securely for {account}")

        # Send notification email
        if send_notification(email):
            st.success("📩 Email notification sent!")


# ----------------------------
# Admin Decrypt Panel
# ----------------------------
st.markdown("---")
st.subheader("Admin Decrypt Tool")

cipher_text = st.text_input("Paste encrypted text", type="password")

if st.button("Decrypt"):
    try:
        plain = fernet.decrypt(cipher_text.encode()).decode()
        st.success(f"Decrypted: {plain}")
    except:
        st.error("Invalid encrypted string")
