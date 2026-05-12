import streamlit as st
import os
from redline.utils.auth import check_password
from redline.utils.prompts import list_available_prompts
from redline.core.config_service import ConfigService

if not check_password():
    st.stop()

st.title("⚙️ Admin Settings")

config_service = ConfigService()

# 1. System Config (Database Backed)
st.subheader("🛠️ System Configuration")
st.info("These settings are stored in MongoDB and override .env file values.")

with st.expander("LLM Settings", expanded=True):
    nv_key = st.text_input("NVIDIA API Key", value=config_service.get("NVIDIA_API_KEY", ""), type="password")
    
    # Recommended Models Dropdown
    recommended_models = {
        "Minimax M2.7 (Current)": "minimaxai/minimax-m2.7",
        "Llama 3.1 405B (Smartest)": "meta/llama-3.1-405b-instruct",
        "Mistral Large 2 (Best Tone)": "mistralai/mistral-large-2-instruct",
        "DeepSeek V3 (Technical)": "deepseek-ai/deepseek-v3",
        "Llama 3.1 70B (Fast/Balanced)": "meta/llama-3.1-70b-instruct"
    }
    
    selected_rec = st.selectbox("Recommended Models", options=list(recommended_models.keys()), index=0)
    default_model = recommended_models[selected_rec]
    
    nv_model = st.text_input("Model ID", value=config_service.get("DEFAULT_LLM_MODEL", default_model))
    if st.button("Save LLM Settings"):
        config_service.set("NVIDIA_API_KEY", nv_key, "API Key for NVIDIA LLM")
        config_service.set("DEFAULT_LLM_MODEL", nv_model, "Primary model used for generations")
        st.success("LLM settings saved to database!")
    
    st.markdown("---")
    if st.button("🧪 Test NVIDIA Connection"):
        if not nv_key:
            st.error("Please enter an API Key first.")
        else:
            try:
                from redline.providers.llm.nvidia_provider import NVIDIAProvider
                with st.spinner("Testing connectivity..."):
                    tester = NVIDIAProvider(nv_key, nv_model)
                    response_data = tester.generate("Hello, respond with 'SUCCESS' if you can read this.")
                    raw_text = response_data.get("raw_text", "No response")
                    if raw_text:
                        st.success(f"NVIDIA API responded: {raw_text}")
                    else:
                        st.error("Received an empty response from NVIDIA.")
            except Exception as e:
                st.error(f"Connection Failed: {str(e)}")

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
        from redline.providers.mongo.client import MongoManager
        db = MongoManager().get_db()
        db.job_runs.delete_many({})
        st.success("Logs purged.")
