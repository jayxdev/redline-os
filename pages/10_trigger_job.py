import streamlit as st
import os
from providers.telegram.client import TelegramClient

st.title("🔗 Remote Trigger")

token = st.query_params.get("token")
job = st.query_params.get("job")

EXPECTED_TOKEN = os.getenv("TRIGGER_TOKEN")

if not token:
    st.error("Access Denied: Missing token.")
    st.stop()

if token != EXPECTED_TOKEN:
    st.error("Access Denied: Invalid token.")
    st.stop()

if not job:
    st.warning("No job specified. Usage: ?token=...&job=daily")
    st.stop()

st.success(f"Triggering job: {job}")

# Placeholder for job execution logic
# 1. Acquire lock
# 2. Start job run record
# 3. Execute steps
# 4. Notify via Telegram
# 5. Update record

st.info(f"Execution logic for '{job}' will be implemented in Phase 4.")

# Telegram Notification Test
if st.button("Send Test Notification"):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if bot_token and chat_id:
        tg = TelegramClient(bot_token, chat_id)
        if tg.send_message(f"🚀 Triggered job: {job} from remote page."):
            st.success("Notification sent!")
        else:
            st.error("Failed to send notification.")
    else:
        st.error("Telegram credentials not found.")
