import streamlit as st
import requests

# Gemini API endpoint and key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

def gemini_generate(prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    params = {"key": GEMINI_API_KEY}
    response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
    if response.status_code == 200:
        completions = response.json()
        answer = completions["candidates"][0]["content"]["parts"][0]["text"]
        return answer.strip()
    else:
        st.error(f"Error fetching Gemini response ({response.status_code}): {response.text}")
        return ""

# ---- Custom CSS for Ikigai themed aesthetics ----
st.markdown(
    """
    <style>
    /* Background and font */
    .main {
        background: linear-gradient(135deg, #d5e3e1, #f2efe8);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Header styling */
    .css-1v3fvcr h1 {
        color: #2c3e50;
        font-weight: 900;
        font-size: 3rem;
        margin-bottom: 0.1em;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #f7f8f9;
        border-radius: 15px;
        padding: 20px;
    }

    /* Buttons */
    button[kind="primary"] {
        background-color: #3a9970 !important;
        color: white !important;
        font-weight: 600;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    button[kind="primary"]:hover {
        background-color: #2c7a51 !important;
    }

    /* Cards for sections */
    .stContainer > div > div {
        background-color: white;
        box-shadow: 0 8px 24px rgba(46, 61, 73, 0.1);
        padding: 20px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    }

    /* Badges */
    .badge {
        background-color: #54b689;
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        margin: 5px 3px;
        display: inline-block;
    }

    /* Questions and answers */
    .qa {
        background-color: #fcfcfd;
        padding: 12px 15px;
        border-radius: 12px;
        margin-bottom: 1em;
        border: 1px solid #d0d6db;
    }

    .qa strong {
        color: #3a9970;
    }
    </style>
    """, unsafe_allow_html=True
)

st.title("🌸 Ikigai-Powered Career Path Advisor")
st.write("*Your Ikigai is the intersection of what you love, what you are good at, what the world needs, and what you can be paid for.*")

with st.sidebar:
    st.header("📝 Your Ikigai Assessment")
    name = st.text_input("Name")
    stage = st.selectbox("Education/Stage", ["High School", "College", "Graduate", "Other"])
    skills = st.text_area("What are you good at?")
    passion = st.text_area("What do you love doing?")
    values = st.text_area("What does the world need from you?")
    rewards = st.text_area("What can you get paid for?")

    if "ikigai_done" not in st.session_state:
        st.session_state.ikigai_done = False
    if "ikigai_result" not in st.session_state:
        st.session_state.ikigai_result = ""
    if "ikigai_careers" not in st.session_state:
        st.session_state.ikigai_careers = []
    if "badges" not in st.session_state:
        st.session_state.badges = set()

    if st.button("Analyze My Ikigai"):
        ikigai_prompt = (f"Based on the Ikigai method, analyze the following user's details and return:\n"
            f"1. An Ikigai description (summary of their purpose)\n"
            f"2. Four career paths that best fit them (bulleted)\n"
            f"User Data:\n"
            f"Name: {name}\n"
            f"Education/Stage: {stage}\n"
            f"Skills: {skills}\n"
            f"Passion: {passion}\n"
            f"Values: {values}\n"
            f"Rewards: {rewards}\n")
        output = gemini_generate(ikigai_prompt)
        st.session_state.ikigai_done = True
        st.session_state.ikigai_result = output

        # Parse careers (simple split)
        if "\n- " in output:
            split_output = output.split("\n- ")
            st.session_state.ikigai_summary = split_output[0]
            careers = [l.strip('- ') for l in split_output[1:]]
            st.session_state.ikigai_careers = careers
        else:
            st.session_state.ikigai_summary = output
            st.session_state.ikigai_careers = []

        st.session_state.badges.add("Ikigai Explorer")

if st.session_state.get("ikigai_done", False):
    st.subheader("🌿 Your Ikigai Profile")
    st.write(st.session_state.ikigai_summary)
    st.write("**🎯 Suggested Careers:**")
    for role in st.session_state.ikigai_careers:
        st.write(f"- {role}")

    st.session_state.badges.add("Career Pathfinder")

    # Personalized upskilling/resources
    st.subheader("📈 Personalized Learning & Upskilling Plan")
    if st.button("Show My Learning Roadmap"):
        upskill_prompt = (f"Suggest 3 skill areas to improve and high-value certification/learning resources. "
                f"Make it specific to this Ikigai: {st.session_state.ikigai_summary} "
                f"and these careers: {', '.join(st.session_state.ikigai_careers)}")
        roadmap = gemini_generate(upskill_prompt)
        st.write(roadmap)
        st.session_state.badges.add("Lifelong Learner")

    # Real-time job suggestions
    st.subheader("💼 Current Market: In-Demand Jobs & Skills")
    if st.button("Suggest Jobs in Demand"):
        jobs_prompt = (f"Based on the latest job market, what are 3 roles and their hottest skills for: {', '.join(st.session_state.ikigai_careers)}?")
        jobs = gemini_generate(jobs_prompt)
        st.write(jobs)
        st.session_state.badges.add("Job Market Navigator")

    # Resume & Cover Letter Generation
    st.subheader("📄 Generate Resume and Cover Letter")
    exp = st.text_area("Describe your experience/goal statement:", key="exp")
    if st.button("Create Resume & Cover Letter"):
        resume_prompt = (f"Using the following experience and Ikigai result, generate a professional resume summary and a cover letter. "
                         f"Ikigai: {st.session_state.ikigai_summary} | Career Target: {', '.join(st.session_state.ikigai_careers)} | "
                         f"Experience: {exp}")
        ai_docs = gemini_generate(resume_prompt)
        st.write(ai_docs)
        st.session_state.badges.add("Resume Crafter")

# --- Interactive AI Career Counselor Chatbot ---
st.subheader("🤖 Ask the Career Counselor Chatbot")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_ques = st.text_input("Your question:", key="chat")
if st.button("Ask Counselor"):
    chat_prompt = (f"You are an expert career advisor using the Ikigai framework. "
                   f"User's Ikigai summary: {st.session_state.get('ikigai_summary','')}\n"
                   f"User's career interests: {', '.join(st.session_state.get('ikigai_careers',[]))}\n"
                   f"User's question: {user_ques}")
    answer = gemini_generate(chat_prompt)
    st.session_state.chat_history.append((user_ques, answer))
    st.session_state.badges.add("Chat Explorer")

for q, a in st.session_state.chat_history:
    st.markdown(f'<div class="qa"><strong>You:</strong> {q}<br><strong>Advisor:</strong> {a}</div>', unsafe_allow_html=True)

# --- Badges/rewards system ---
st.sidebar.header("🏅 Your Badges")
for badge in st.session_state.badges:
    st.sidebar.markdown(f'<div class="badge">{badge}</div>', unsafe_allow_html=True)

st.sidebar.subheader("🎓 Progress")
st.sidebar.info(f"Badges earned: {len(st.session_state.badges)}")
