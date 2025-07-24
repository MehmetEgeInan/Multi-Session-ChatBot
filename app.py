import streamlit as st
from chatbot import ChatBot
import pandas as pd
import uuid

# Sayfa ayarları
st.set_page_config(
    page_title="Çoklu Oturumlu ChatBot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Stilleri
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background: #1e1e1e !important;
    }
    .stChatInput {
        position: fixed;
        bottom: 20px;
        width: 60%;
        background: #2d2d2d !important;
    }
    .session-item {
        padding: 8px;
        margin: 4px 0;
        border-radius: 5px;
        cursor: pointer;
    }
    .session-item:hover {
        background: #333333;
    }
    .active-session {
        background: #444444 !important;
        border-left: 3px solid #4f8bf9;
    }
    .delete-btn {
        color: #ff4b4b !important;
        padding: 0 8px !important;
    }
    .stDataFrame {
        background: transparent !important;
    }
    table {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Oturum yönetimi
if 'current_session' not in st.session_state:
    st.session_state.current_session = str(uuid.uuid4())
    ChatBot(st.session_state.current_session)  # Yeni oturum oluştur

if 'bot' not in st.session_state:
    st.session_state.bot = ChatBot(st.session_state.current_session)

# Sidebar - Oturum Yönetimi
with st.sidebar:
    st.title("🗂 Oturumlar")
    
    # Yeni oturum butonu
    if st.button("➕ Yeni Oturum", use_container_width=True, key="new_session"):
        new_id = str(uuid.uuid4())
        ChatBot.create_new_session()
        st.session_state.current_session = new_id
        st.session_state.bot = ChatBot(new_id)
        st.rerun()
    
    st.markdown("---")
    
    # Oturum listesi
    sessions = ChatBot.get_all_sessions()
    for session_id, name, last_used in sessions:
        session_container = st.container()
        
        with session_container:
            cols = st.columns([5, 1])
            with cols[0]:
                if st.button(
                    f"💬 {name}",
                    key=f"select_{session_id}",
                    help=f"Son kullanım: {last_used}",
                    use_container_width=True
                ):
                    if st.session_state.current_session != session_id:
                        st.session_state.current_session = session_id
                        st.session_state.bot = ChatBot(session_id)
                        st.rerun()
            
            with cols[1]:
                if st.button(
                    "❌", 
                    key=f"delete_{session_id}",
                    help="Bu oturumu sil",
                    type="secondary"
                ):
                    if len(sessions) > 1:
                        ChatBot.delete_session(session_id)
                        if st.session_state.current_session == session_id:
                            # Silinen oturum aktifse ilk oturuma geç
                            st.session_state.current_session = sessions[0][0]
                        st.rerun()
                    else:
                        st.error("Son oturumu silemezsiniz")

    st.markdown("---")
    
    # Seçili oturumun geçmişi
    current_session_name = next(
        (name for id, name, lu in sessions if id == st.session_state.current_session),
        "Yeni Sohbet"
    )
    st.markdown(f"**Geçmiş: {current_session_name}**")
    
    history = st.session_state.bot.get_history()
    if history:
        df = pd.DataFrame(history, columns=["Rol", "Mesaj", "Saat"])
        st.dataframe(
            df[["Saat", "Rol", "Mesaj"]],
            use_container_width=True,
            hide_index=True,
            height=300
        )
    else:
        st.info("Bu oturumda mesaj yok")

# Ana sayfa
st.title(f"💬 {current_session_name}")

# Mesaj geçmişini göster
for role, content, _ in st.session_state.bot.get_history():
    with st.chat_message(role):
        st.markdown(content)

# Mesaj girişi
if prompt := st.chat_input("Mesajınızı yazın..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Yanıt oluşturuluyor..."):
        response = st.session_state.bot.chat(prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.rerun()