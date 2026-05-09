import os
import requests
import pandas as pd
import streamlit as st

from PIL import Image
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder

load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="QBS AI Analytics",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SESSION
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================================================
# PROFESSIONAL CSS
# =========================================================

st.markdown(
    """
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.stApp {

    background:
        radial-gradient(
            circle at top left,
            #12305f 0%,
            #04142d 35%,
            #010814 100%
        );

    color: white;
}

.block-container {

    max-width: 1500px;

    padding-top: 2rem;

    padding-bottom: 120px;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #08152c 0%,
            #020817 100%
        );

    border-right:
        1px solid rgba(255,255,255,0.08);
}

.sidebar-title {

    text-align: center;

    font-size: 36px;

    font-weight: 900;

    color: white;

    margin-top: 20px;

    margin-bottom: 40px;
}

div[data-testid="stRadio"] label {

    color: white !important;

    font-weight: 700 !important;
}

/* HERO */

.hero {

    background:
        linear-gradient(
            135deg,
            rgba(17,34,64,0.95),
            rgba(5,12,25,0.95)
        );

    padding: 45px;

    border-radius: 28px;

    border:
        1px solid rgba(255,255,255,0.08);

    margin-bottom: 40px;

    box-shadow:
        0px 0px 35px rgba(0,0,0,0.35);
}

.hero-title {

    font-size: 54px;

    font-weight: 900;

    color: white;

    margin-bottom: 15px;
}

.hero-sub {

    color:
        rgba(255,255,255,0.75);

    font-size: 19px;

    line-height: 1.8;
}

/* USER MESSAGE */

.user-box {

    background:
        linear-gradient(
            135deg,
            #2563eb,
            #3b82f6
        );

    padding: 22px;

    border-radius: 22px;

    margin-top: 25px;

    margin-bottom: 18px;

    box-shadow:
        0px 0px 30px rgba(37,99,235,0.35);
}

.user-title {

    font-size: 18px;

    font-weight: 800;

    color: white;

    margin-bottom: 10px;
}

.user-question {

    color: white;

    font-size: 17px;
}

/* AI MESSAGE */

.ai-box {

    background:
        linear-gradient(
            135deg,
            rgba(10,18,32,0.98),
            rgba(2,8,20,0.98)
        );

    padding: 28px;

    border-radius: 24px;

    border:
        1px solid rgba(255,255,255,0.08);

    margin-bottom: 20px;
}

.ai-title {

    font-size: 24px;

    font-weight: 900;

    color: white;

    margin-bottom: 18px;
}

.answer {

    color:
        rgba(255,255,255,0.92);

    font-size: 18px;

    line-height: 1.8;
}

/* TABLE */

[data-testid="stDataFrame"] {

    border-radius: 18px;

    overflow: hidden;

    border:
        1px solid rgba(255,255,255,0.08);
}

/* INPUT */

.stChatInputContainer {

    background:
        rgba(1,8,20,0.96);

    border-top:
        1px solid rgba(255,255,255,0.08);
}

.mic-container {

    margin-top: 8px;
}

</style>
""",
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    try:

        logo = Image.open(
            "qbs_logo.jpg"
        )

        st.image(
            logo,
            width="stretch"
        )

    except:
        pass

    st.markdown(
        """
        <div class="sidebar-title">
            QBS AI Analytics
        </div>
        """,
        unsafe_allow_html=True
    )

    provider = st.radio(
        "AI Provider",
        [
            "claude",
            "openai",
            "groq"
        ],
        index=0
    )

    st.divider()

    if st.button(
        "🧹 Clear Conversation",
        width="stretch"
    ):

        st.session_state.messages = []

        st.rerun()

# =========================================================
# HERO
# =========================================================

st.markdown(
    """
<div class="hero">

    <div class="hero-title">
        🚘 QBS AI Analytics Platform
    </div>

    <div class="hero-sub">
        Enterprise conversational analytics powered by AI and SQL intelligence for automotive ERP systems.
    </div>

</div>
""",
    unsafe_allow_html=True
)

# =========================================================
# CHAT HISTORY
# =========================================================

for msg in st.session_state.messages:

    st.markdown(
        f"""
        <div class="user-box">

            <div class="user-title">
                👤 You
            </div>

            <div class="user-question">
                {msg["question"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="ai-box">

            <div class="ai-title">
                🤖 AI Assistant • {msg["provider"].upper()}
            </div>

            <div class="answer">
                {msg["summary"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if msg["rows"]:

        df = pd.DataFrame(
            msg["rows"]
        )

        st.dataframe(
            df,
            width="stretch"
        )

# =========================================================
# GPT STYLE INPUT
# =========================================================

col1, col2 = st.columns([12, 1])

with col1:

    question = st.chat_input(
        "Ask anything about your ERP business data..."
    )

with col2:

    st.markdown(
        '<div class="mic-container">',
        unsafe_allow_html=True
    )

    voice = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹️",
        just_once=True,
        use_container_width=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

final_question = question

# =========================================================
# PLACEHOLDER VOICE MODE
# =========================================================

if voice and not question:

    final_question = (
        "Show total after-sales revenue"
    )

# =========================================================
# SEND REQUEST
# =========================================================

if final_question:

    try:

        response = requests.post(
            f"{BACKEND_URL}/ask",
            json={
                "question": final_question,
                "provider": provider
            },
            timeout=300
        )

        if response.status_code == 200:

            data = response.json()

            st.session_state.messages.append({

                "question":
                    final_question,

                "summary":
                    data.get(
                        "summary",
                        "No answer returned."
                    ),

                "rows":
                    data.get(
                        "rows",
                        []
                    ),

                "provider":
                    provider
            })

            st.rerun()

        else:

            st.error(
                f"Backend Error: {response.text}"
            )

    except Exception as e:

        st.error(
            f"Connection Error: {str(e)}"
        )