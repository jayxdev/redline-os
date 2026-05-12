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
    
    # 1. Load Favorites from DB
    import json
    fav_json = config_service.get("FAVORITE_MODELS", "{}")
    try:
        favorites = json.loads(fav_json)
    except:
        favorites = {}

    # 2. Merge Options (Favorites + Live Sync Only)
    display_options = {}
    for name, mid in favorites.items():
        display_options[f"⭐ {name}"] = mid
    
    if "fetched_models_dict" in st.session_state:
        for name, mid in st.session_state.fetched_models_dict.items():
            if mid not in display_options.values():
                display_options[f"✨ {name}"] = mid

    # Selection logic (Robust handling)
    def on_model_select():
        key = st.session_state.get("selected_rec_key")
        if key in display_options:
            st.session_state.nv_model_input = display_options[key]

    if display_options:
        st.selectbox(
            "Model Selection (Favorites + Live)", 
            options=list(display_options.keys()), 
            key="selected_rec_key",
            on_change=on_model_select
        )
    else:
        st.warning("No models found. Hit 'Sync Live Catalog' below to discover models.")
    
    if "nv_model_input" not in st.session_state:
        # Fallback to current saved model if it exists, otherwise empty
        st.session_state.nv_model_input = config_service.get("DEFAULT_LLM_MODEL", "")

    nv_model = st.text_input("Model ID", key="nv_model_input")
    
    col_save, col_fav = st.columns([1, 1])
    with col_save:
        if st.button("💾 Save as Default", use_container_width=True):
            config_service.set("NVIDIA_API_KEY", nv_key, "API Key for NVIDIA LLM")
            config_service.set("DEFAULT_LLM_MODEL", nv_model, "Primary model used for generations")
            st.success("Settings Saved!")
    
    with col_fav:
        if st.button("⭐ Add to Favorites", use_container_width=True):
            # Clean up name for favorite
            fav_name = nv_model.split("/")[-1].replace("-", " ").title()
            favorites[fav_name] = nv_model
            config_service.set("FAVORITE_MODELS", json.dumps(favorites), "List of bookmarked models")
            st.success(f"Added {fav_name} to Favorites!")
            st.rerun()

    if favorites:
        with st.expander("🗑️ Manage Favorites"):
            for name, mid in list(favorites.items()):
                col_n, col_d = st.columns([3, 1])
                col_n.write(f"**{name}**: `{mid}`")
                if col_d.button("Remove", key=f"del_{mid}"):
                    del favorites[name]
                    config_service.set("FAVORITE_MODELS", json.dumps(favorites))
                    st.rerun()
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧪 Test Connection"):
            if not nv_key: st.error("Enter API Key.")
            else:
                try:
                    from redline.providers.llm.nvidia_provider import NVIDIAProvider
                    with st.spinner("Testing..."):
                        tester = NVIDIAProvider(nv_key, nv_model)
                        res = tester.generate("Hello")
                        if res.get("raw_text"): st.success("Verified! ✅")
                        else: st.error("No response.")
                except Exception as e: st.error(f"Error: {str(e)}")
    
    with col2:
        if st.button("🔄 Sync Live Catalog"):
            if not nv_key: st.error("Enter API Key.")
            else:
                try:
                    import requests
                    headers = {"Authorization": f"Bearer {nv_key}"}
                    res = requests.get("https://integrate.api.nvidia.com/v1/models", headers=headers, timeout=10)
                    if res.status_code == 200:
                        models_data = res.json().get("data", [])
                        fetched = {}
                        for m in models_data:
                            mid = m["id"]
                            name = mid.split("/")[-1].replace("-", " ").title()
                            fetched[name] = mid
                        st.session_state.fetched_models_dict = fetched
                        st.success(f"Sync Complete! {len(fetched)} found.")
                        st.rerun()
                    else: st.error(f"Error: {res.status_code}")
                except Exception as e: st.error(f"Error: {str(e)}")

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
