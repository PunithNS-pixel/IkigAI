import streamlit as st
import requests
import uuid

# Set up session state for persistent user data
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'badge_list' not in st.session_state:
    st.session_state.badge_list = []
if 'ikigai_result' not in st.session_state:
    st.session_state.ikigai_result = {}
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

st.title("Ikigai-Powered Career Path Advisor")
st.write("Unlock your true potential with personalized career guidance based on your Ikigai.")

# ---- IKIGAI INPUT ----
with st.sidebar:
    st.header("Your Ikigai Assessment")
    st.session_state.user_profile['name'] = st.text_input("Name")
    st.session_state.user_profile['stage'] = st.selectbox("Education/Stage", ["High School", "College", "Graduate", "Other"])
    st.session_state.user_profile['skills'] = st.text_area("What are you good at?")
    st.session_state.user_profile['passion'] = st.text_area("What do you love doing?")
    st.session_state.user_profile['values'] = st.text_area("What does the world need from you?")
    st.session_state.user_profile['rewards'] = st.text_area("What can you get paid for?")
    if st.button("Find my Ikigai"):
        payload = {
            "prompt": f"Based on this student's Ikigai \nSkills: {st.session_state.user_profile['skills']}\nPassion: {st.session_state.user_profile['passion']}\nValues: {st.session_state.user_profile['values']}\nRewards: {st.session_state.user_profile['rewards']}\nSuggest suitable career options and a plan.",
            "apiKey": st.secrets["GEMINI_API_KEY"],
        }
        # Replace with call to Google Gemini/GenAI
        # Here's a placeholder for actual AI response:
        st.session_state.ikigai_result = {
            "summary": "You are best suited for creative, socially impactful roles that combine your tech skills and passion for helping others.",
            "careers": ["Data Scientist for Social Good", "Educational Technology Consultant", "AI Researcher", "Mental Health Tech Innovator"]
        }
        if "ikigai_finder" not in st.session_state.badge_list:
            st.session_state.badge_list.append("Ikigai Explorer")

# ---- OUTPUT DASHBOARD ----
if st.session_state.ikigai_result:
    st.success("Your Ikigai Profile Identified!")
    st.write(st.session_state.ikigai_result["summary"])
    st.subheader("Recommended Careers")
    for career in st.session_state.ikigai_result["careers"]:
        st.write(f"- {career}")

    # Resource Links & Roadmap
    st.subheader("Roadmap & Upskilling Resources")
    st.write("Explore curated resources, learning paths, and certification tracks tailored to your Ikigai.")
    st.write("[Sample Resource: Coursera Data Science for Social Good](https://coursera.org)")
    st.write("[Sample Resource: Google Career Certificates](https://grow.google/)")

    if st.button("Enroll in a Track"):
        st.info("Enrollment recorded. You have unlocked the 'Lifelong Learner' badge!")
        if "lifelong_learner" not in st.session_state.badge_list:
            st.session_state.badge_list.append("Lifelong Learner")

    # Job & Trend Analysis
    st.subheader("In-Demand Jobs & Skills")
    st.write("Based on current labor market data, the most in-demand roles are:")
    st.write("- AI Solutions Architect")
    st.write("- Digital Wellness Counselor")

    # Resume Generator
    st.subheader("AI Resume/Cover Letter Generator")
    exp = st.text_area("Describe your experience and aspirations for your resume/cover letter:")
    if st.button("Generate Resume/Cover Letter"):
        # Placeholder
        st.write("Your tailored resume/cover letter will be ready for download shortly (Google Gemini integration needed).")
        if "resume_builder" not in st.session_state.badge_list:
            st.session_state.badge_list.append("Resume Builder")

# ---- Chatbot ----
st.subheader("Ask the Career Counselor Bot")
user_input = st.text_input("Your question:")
if st.button("Ask Bot") and user_input:
    # Replace with Gemini API call for chatbot response
    chatbot_response = f"(Simulated) AI Response: Great question! For {user_input}, consider..."
    st.session_state.conversation_history.append({"q": user_input, "a": chatbot_response})
    if "first_chat" not in st.session_state.badge_list:
        st.session_state.badge_list.append("First Interaction")
for chat in st.session_state.conversation_history:
    st.write(f"**Q:** {chat['q']}\n**A:** {chat['a']}")

# ---- Badges ----
st.sidebar.header("Your Badges")
for badge in st.session_state.badge_list:
    st.sidebar.success(f"🏅 {badge}")

# ---- User Progress Tracking ----
st.sidebar.subheader("Your Progress")
progress_info = f"Completed: {len(st.session_state.badge_list)} missions"
st.sidebar.info(progress_info)
