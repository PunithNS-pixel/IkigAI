import streamlit as st
import requests
import json

# Gemini API endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
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

st.title("Ikigai-Powered Career Path Advisor")
st.write("Find your ideal career path using the Japanese technique of Ikigai and the power of Google AI.")

with st.sidebar:
    st.header("Your Ikigai Assessment")
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
    st.subheader("Your Ikigai Profile")
    st.write(st.session_state.ikigai_summary)
    st.write("**Suggested careers:**")
    for role in st.session_state.ikigai_careers:
        st.write(f"- {role}")

    st.session_state.badges.add("Career Pathfinder")

    # Personalized upskilling/resources
    st.subheader("Personalized Learning & Upskilling Plan")
    if st.button("Show My Learning Roadmap"):
        upskill_prompt = (f"Suggest 3 skill areas to improve and high-value certification/learning resources. "
                f"Make it specific to this Ikigai: {st.session_state.ikigai_summary} "
                f"and these careers: {', '.join(st.session_state.ikigai_careers)}")
        roadmap = gemini_generate(upskill_prompt)
        st.write(roadmap)
        st.session_state.badges.add("Lifelong Learner")

    # Real-time job suggestions
    st.subheader("Current Market: In-Demand Jobs & Skills")
    if st.button("Suggest Jobs in Demand"):
        jobs_prompt = (f"Based on the latest job market, what are 3 roles and their hottest skills for: {', '.join(st.session_state.ikigai_careers)}?")
        jobs = gemini_generate(jobs_prompt)
        st.write(jobs)
        st.session_state.badges.add("Job Market Navigator")

    # Resume & Cover Letter Generation
    st.subheader("Generate Resume and Cover Letter")
    exp = st.text_area("Describe your experience/goal statement:", key="exp")
    if st.button("Create Resume & Cover Letter"):
        resume_prompt = (f"Using the following experience and Ikigai result, generate a professional resume summary and a cover letter. "
                         f"Ikigai: {st.session_state.ikigai_summary} | Career Target: {', '.join(st.session_state.ikigai_careers)} | "
                         f"Experience: {exp}")
        ai_docs = gemini_generate(resume_prompt)
        st.write(ai_docs)
        st.session_state.badges.add("Resume Crafter")

# --- Interactive AI Career Counselor Chatbot ---
st.subheader("Ask the Career Counselor Chatbot")
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
    st.markdown(f"**You:** {q}\n\n**Advisor:** {a}")

# --- Badges/rewards system ---
st.sidebar.header("Your Badges")
for badge in st.session_state.badges:
    st.sidebar.success(f"🏅 {badge}")

st.sidebar.subheader("Progress")
st.sidebar.info(f"Badges earned: {len(st.session_state.badges)}")
