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
    
    # Recommended Models Mapping (Verified Active 2026)
    recommended_models = {
        "Llama 3.3 Super (Fastest/Smartest)": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "Llama 3.1 70B (Reliable)": "meta/llama-3.1-70b-instruct",
        "Minimax M2.7 (Deep Reasoning)": "minimaxai/minimax-m2.7"
    }
    
    # Selection logic
    def update_model_id():
        st.session_state.nv_model_input = recommended_models[st.session_state.selected_rec_key]

    selected_rec = st.selectbox(
        "Recommended Models", 
        options=list(recommended_models.keys()), 
        key="selected_rec_key",
        on_change=update_model_id
    )
    
    if "nv_model_input" not in st.session_state:
        st.session_state.nv_model_input = config_service.get("DEFAULT_LLM_MODEL", recommended_models[selected_rec])

    nv_model = st.text_input("Model ID", key="nv_model_input")
    if st.button("Save LLM Settings"):
        config_service.set("NVIDIA_API_KEY", nv_key, "API Key for NVIDIA LLM")
        config_service.set("DEFAULT_LLM_MODEL", nv_model, "Primary model used for generations")
        st.success("LLM settings saved to database!")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧪 Test Connection"):
            if not nv_key:
                st.error("Please enter an API Key first.")
            else:
                try:
                    from redline.providers.llm.nvidia_provider import NVIDIAProvider
                    with st.spinner("Testing..."):
                        tester = NVIDIAProvider(nv_key, nv_model)
                        response_data = tester.generate("Hello, respond with 'SUCCESS' if you can read this.")
                        raw_text = response_data.get("raw_text", "No response")
                        if raw_text: st.success(f"NVIDIA API responded: {raw_text}")
                        else: st.error("Received an empty response.")
                except Exception as e:
                    st.error(f"Connection Failed: {str(e)}")
    
    with col2:
        if st.button("🔄 Fetch Latest Models"):
            if not nv_key:
                st.error("Enter API Key to fetch models.")
            else:
                try:
                    import requests
                    headers = {"Authorization": f"Bearer {nv_key}"}
                    response = requests.get("https://integrate.api.nvidia.com/v1/models", headers=headers, timeout=10)
                    if response.status_code == 200:
                        models_data = response.json().get("data", [])
                        # Filter for interesting chat models
                        chat_models = [m["id"] for m in models_data if "instruct" in m["id"].lower() or "chat" in m["id"].lower() or "super" in m["id"].lower()]
                        st.session_state.fetched_models = sorted(chat_models)
                        st.success(f"Found {len(chat_models)} active chat models!")
                    else:
                        st.error(f"Failed to fetch models: {response.status_code}")
                except Exception as e:
                    st.error(f"Fetch Error: {str(e)}")

    if "fetched_models" in st.session_state:
        st.info("Available Models (Copy/Paste into 'Model ID' above):")
        st.code("\n".join(st.session_state.fetched_models))
        if st.button("Clear Fetched List"):
            del st.session_state.fetched_models
            st.rerun()

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
