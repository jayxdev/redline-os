import streamlit as st
import os
from cloud_build.utils.auth import check_password
from cloud_build.utils.prompts import list_available_prompts
from cloud_build.core.config_service import ConfigService

if not check_password():
    st.stop()

st.title("⚙️ Admin Settings")

config_service = ConfigService()

# 1. System Config (Database Backed)
st.subheader("🛠️ System Configuration")
st.info("These settings are stored in MongoDB and override .env file values.")

with st.expander("LLM Settings", expanded=True):
    nv_key = st.text_input("NVIDIA API Key", value=config_service.get("NVIDIA_API_KEY", ""), type="password")
    nv_model = st.text_input("Default LLM Model", value=config_service.get("DEFAULT_LLM_MODEL", "meta/llama-3-70b-instruct"))
    if st.button("Save LLM Settings"):
        config_service.set("NVIDIA_API_KEY", nv_key, "API Key for NVIDIA LLM")
        config_service.set("DEFAULT_LLM_MODEL", nv_model, "Primary model used for generations")
        st.success("LLM settings saved to database!")

with st.expander("Telegram Settings", expanded=False):
    tg_token = st.text_input("Bot Token", value=config_service.get("TELEGRAM_BOT_TOKEN", ""), type="password")
    tg_chat = st.text_input("Chat ID", value=config_service.get("TELEGRAM_CHAT_ID", ""))
    if st.button("Save Telegram Settings"):
        config_service.set("TELEGRAM_BOT_TOKEN", tg_token, "Telegram bot auth token")
        config_service.set("TELEGRAM_CHAT_ID", tg_chat, "Target chat ID for notifications")
        st.success("Telegram settings saved to database!")

with st.expander("Security Settings", expanded=False):
    trigger_token = st.text_input("Trigger Token", value=config_service.get("TRIGGER_TOKEN", ""), type="password")
    if st.button("Save Security Settings"):
        config_service.set("TRIGGER_TOKEN", trigger_token, "Secret for protected trigger page")
        st.success("Security settings saved!")

with st.expander("Regional Settings", expanded=False):
    app_tz = st.text_input("System Timezone", value=config_service.get("APP_TIMEZONE", "UTC"))
    if st.button("Save Regional Settings"):
        config_service.set("APP_TIMEZONE", app_tz, "System display timezone")
        st.success("Timezone updated!")

st.divider()

# 2. Existing Info Sections
with st.expander("Prompt Templates"):
    st.write("Available prompts in repo:")
    prompts = list_available_prompts()
    for p in prompts:
        st.code(p)

with st.expander("System Reset / Maintenance", expanded=False):
    st.warning("These actions are destructive.")
    if st.button("Purge Job Logs"):
        from cloud_build.providers.mongo.client import MongoManager
        db = MongoManager().get_db()
        db.job_runs.delete_many({})
        st.success("Logs purged.")
