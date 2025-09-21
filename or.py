import streamlit as st
import datetime
import pandas as pd
import requests
import time
import sqlite3
from textblob import TextBlob

st.set_page_config(
    page_title="Parmatma - Health & Wellness Tracker",
    page_icon="🧘‍♂️",
    layout="centered"
)

# ------------------ Database Setup ------------------

DB_PATH = "parmatma.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT,
                       age
                       INTEGER,
                       gender
                       TEXT,
                       height
                       REAL,
                       weight
                       REAL,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS symptom_entries
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER,
                       symptoms
                       TEXT,
                       response
                       TEXT,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS mental_health_entries
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER,
                       mood_note
                       TEXT,
                       sentiment
                       REAL,
                       response
                       TEXT,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   """)
    conn.commit()
    conn.close()


init_db()


def save_personal_details_to_db(details):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, age, gender, height, weight) VALUES (?, ?, ?, ?, ?)",
        (details['name'], details['age'], details['gender'], details['height'], details['weight'])
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def save_symptom_entry(user_id, symptoms, response):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO symptom_entries (user_id, symptoms, response) VALUES (?, ?, ?)",
        (user_id, symptoms, response)
    )
    conn.commit()
    conn.close()


def save_mental_health_entry(user_id, mood_note, sentiment, response):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mental_health_entries (user_id, mood_note, sentiment, response) VALUES (?, ?, ?, ?)",
        (user_id, mood_note, sentiment, response)
    )
    conn.commit()
    conn.close()


def load_user_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM symptom_entries WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    symptoms = cursor.fetchall()
    cursor.execute("SELECT * FROM mental_health_entries WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    mental = cursor.fetchall()
    conn.close()
    return symptoms, mental


# ------------------ Helper Functions ------------------

def google_api_call(model, endpoint, payload):
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("Google API key missing. Please add it to secrets.toml")
        st.stop()
    api_key = st.secrets["GOOGLE_API_KEY"]
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:{endpoint}?key={api_key}"
    retries, max_retries, delay = 0, 3, 1
    while retries < max_retries:
        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            if response.status_code == 429:
                retries += 1
                time.sleep(delay)
                delay *= 2
            else:
                raise err
        except Exception as e:
            raise e
    raise Exception("Max retries exceeded for API call.")


def calculate_bmi_and_category(weight_kg, height_cm):
    if height_cm <= 0 or weight_kg <= 0:
        return 0, "Invalid", "Height and weight must be positive numbers."
    bmi = weight_kg / ((height_cm / 100) ** 2)
    if bmi < 18.5:
        category, advice = "Underweight", "Focus on nutrient-dense foods and consult a professional for healthy weight gain."
    elif 18.5 <= bmi < 25:
        category, advice = "Normal", "Maintain balanced diet and regular exercise."
    elif 25 <= bmi < 30:
        category, advice = "Overweight", "Consider a balanced diet and increase activity."
    else:
        category, advice = "Obese", "Consult a professional for personalized weight management."
    return bmi, category, advice


# Mock free symptom checker (replace with real API integration)
def infermedica_symptom_checker(symptom_text):
    # For demo purposes, returns canned response
    return ("Possible causes: Common cold, flu. Advice: Rest, hydrate, see doctor if symptoms worsen.",
            [{"title": "Common Cold", "uri": "https://www.cdc.gov/common-cold/"},
             {"title": "Flu", "uri": "https://www.cdc.gov/flu/"}])


# ------------------- Pages ---------------------------

def home_page():
    st.title("Welcome to Parmatma 🧘‍♂️")
    st.markdown("Your all-in-one health and wellness companion.")
    with st.container():
        st.subheader("Personal Details")
        with st.form("personal_details_form"):
            name = st.text_input("Name")
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", min_value=5, max_value=120, step=1)
            with col2:
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, format="%.2f")
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, format="%.2f")
            submitted = st.form_submit_button("Submit Details")
            if submitted:
                if not name:
                    st.error("Please enter your name.")
                elif height <= 0 or weight <= 0:
                    st.error("Height and weight must be positive.")
                else:
                    details = {
                        'name': name, 'age': age, 'gender': gender,
                        'height': height, 'weight': weight
                    }
                    user_id = save_personal_details_to_db(details)
                    st.session_state['user_id'] = user_id
                    st.session_state['personal'] = details
                    bmi, category, advice = calculate_bmi_and_category(weight, height)
                    st.session_state['bmi_category'] = category
                    st.success(f"Hello {name}! Details saved and stored. You can now use all features.")


def bmi_calculator_page():
    st.header("BMI Calculator ⚖️")
    personal = st.session_state.get('personal')
    if not personal:
        st.info("Enter personal details in Home first.")
        return
    bmi, category, advice = calculate_bmi_and_category(personal['weight'], personal['height'])
    st.metric(label="BMI", value=f"{bmi:.2f}")
    if category == "Normal":
        st.success(f"Category: *{category}*\n\n{advice}")
    elif category in ["Overweight", "Underweight"]:
        st.warning(f"Category: *{category}*\n\n{advice}")
    else:
        st.error(f"Category: *{category}*\n\n{advice}")
    if personal['age'] < 18:
        st.write("🧑‍⚕️ For minors, consult a healthcare professional.")


def nutrition_coach_page():
    st.header("Nutrition Coach & Diet Plans 🍏")
    personal = st.session_state.get('personal')
    if not personal:
        st.info("Enter personal details in Home first.")
        return

    bmi_category = st.session_state.get('bmi_category', "Unknown")
    st.markdown(f"**Detected BMI Category:** {bmi_category}")

    if bmi_category == "Underweight":
        base_goal = "weekly meal plan for healthy weight gain"
    elif bmi_category in ["Overweight", "Obese"]:
        base_goal = "weekly fat loss meal plan"
    else:
        base_goal = st.text_input("Enter your nutrition/diet goal:",
                                  placeholder="e.g., 'Balanced weekly diet plan'")

    if st.button("Get Nutrition Plan"):
        if bmi_category in ["Underweight", "Overweight", "Obese"]:
            user_goal = base_goal
        else:
            if not base_goal:
                st.error("Please enter your nutrition or diet goal.")
                return
            user_goal = base_goal

        with st.spinner("Preparing weekly nutrition plan..."):
            user_prompt = f"Create a detailed weekly nutrition plan for: {user_goal}. Use markdown and provide actionable advice."
            payload = {
                "contents": [{"parts": [{"text": user_prompt}]}],
                "systemInstruction": {"parts": [
                    {"text": "Reply as a professional nutritionist. Use markdown."}
                ]}
            }
            response = google_api_call(
                model="gemini-2.5-flash-preview-05-20",
                endpoint="generateContent",
                payload=payload,
            )
            if response and response.get('candidates'):
                generated_text = response['candidates'][0]['content']['parts'][0]['text']
                st.subheader("Your Weekly Nutrition Plan")
                st.write(generated_text)
            else:
                st.error("Failed to generate nutrition plan.")


def exercise_routines_page():
    st.header("Exercise Routines & Fitness Plans 🏃")
    personal = st.session_state.get('personal')
    if not personal:
        st.info("Enter personal details in Home first.")
        return

    gender = personal.get('gender', "Other")
    body_parts = st.multiselect("Select body parts to train:",
                                ["Arms", "Legs", "Core", "Back", "Chest", "Full Body"])
    fitness_goal = st.text_input("Your fitness goal:",
                                 placeholder="e.g., 'Strength training routine for beginners.'")

    if st.button("Get Exercise Routine"):
        if not fitness_goal:
            st.error("Enter your fitness goal.")
            return
        if not body_parts:
            st.error("Select at least one body part to train.")
            return
        with st.spinner("Generating exercise plan..."):
            body_parts_text = ", ".join(body_parts)
            user_prompt = (f"Create a list of 5 engaging exercises to train {body_parts_text} for a {gender} user. "
                           f"Include a timer suggestion to complete each exercise.")
            payload = {
                "contents": [{"parts": [{"text": user_prompt}]}],
                "systemInstruction": {"parts": [
                    {"text": "Reply as a professional trainer. Use markdown."}
                ]}
            }
            response = google_api_call(
                model="gemini-2.5-flash-preview-05-20",
                endpoint="generateContent",
                payload=payload
            )
            if response and response.get('candidates'):
                exercises_text = response['candidates'][0]['content']['parts'][0]['text']
                st.markdown("### Your Exercise Routine")
                st.markdown(exercises_text)

                st.markdown("### Fitness Timer")
                for i in range(5):
                    if st.button(f"Start Exercise {i + 1} Timer (30 sec)"):
                        for sec in range(30, 0, -1):
                            st.write(f"Time left: {sec} seconds")
                            time.sleep(1)
                        st.write("Done! Take a short break.")
            else:
                st.error("Failed to generate routine.")


def symptom_checker_page():
    st.header("Symptom Checker 🩺")
    symptoms = st.text_area("Describe your symptoms:", placeholder="e.g., 'I have fever, headache and cough.'")
    if st.button("Analyze Symptoms"):
        if not symptoms:
            st.error("Please describe your symptoms.")
            return
        with st.spinner("Analyzing symptoms..."):
            message, sources = infermedica_symptom_checker(symptoms)
            st.write(message)
            if sources:
                st.subheader("Sources")
                for i, s in enumerate(sources):
                    st.markdown(f"*{i + 1}.* [{s['title']}]({s['uri']})")
            user_id = st.session_state.get('user_id')
            if user_id:
                save_symptom_entry(user_id, symptoms, message)


def mental_health_page():
    st.header("Mental Health Support ❤️‍🩹")
    st.write("Track your mood and get support. Not a substitute for professional help.")
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = []
    with st.container():
        st.markdown("### New Entry")
        with st.form("journal_entry_form"):
            mood_note = st.text_area("How are you feeling today? (write freely)")
            submitted = st.form_submit_button("Save & Get Advice")
            if submitted:
                if not mood_note.strip():
                    st.error("Please share your thoughts or feelings.")
                else:
                    sentiment = TextBlob(mood_note).sentiment.polarity
                    user_id = st.session_state.get('user_id')
                    with st.spinner("Getting advice..."):
                        user_prompt = (f"Sentiment score: {sentiment:.2f}. User note: {mood_note}. "
                                       "Provide kind, supportive life advice tailored to sentiment.")
                        payload = {
                            "contents": [{"parts": [{"text": user_prompt}]}],
                            "systemInstruction": {"parts": [
                                {"text": "Act as a kind, supportive life coach. Include disclaimer."}
                            ]}
                        }
                        response = google_api_call(
                            model="gemini-2.5-flash-preview-05-20",
                            endpoint="generateContent",
                            payload=payload
                        )
                        if response and response.get('candidates'):
                            ai_response = response['candidates'][0]['content']['parts'][0]['text']
                            st.success("Entry saved!")
                            st.markdown("---")
                            st.subheader("Support & Advice")
                            st.write(ai_response)
                            if user_id:
                                save_mental_health_entry(user_id, mood_note, sentiment, ai_response)
                        else:
                            st.error("Failed to generate advice.")
                    st.experimental_rerun()
    st.markdown("---")
    st.subheader("Past Entries and Sentiment Trend")
    if st.session_state.journal_entries:
        df = pd.DataFrame(st.session_state.journal_entries)
        st.line_chart(df['sentiment'])
        for entry in reversed(st.session_state.journal_entries):
            with st.expander(f"*{entry['date']} - Sentiment: {entry['sentiment']:.2f}*"):
                st.write(f"*Note:* {entry['mood_note']}")
    else:
        st.info("No entries yet.")


def doctor_appointments_page():
    st.header("Doctor Appointments & Telemedicine 🏥")
    st.write("Use symptom checker, get advice, and book appointments.")
    location = st.text_input("Your city or locality for nearby doctors:")
    specialty = st.selectbox("Specialty", ["General", "Cardiologist", "Dermatologist", "Dentist", "Other"])
    if st.button("Find Nearby Doctor"):
        if not location:
            st.error("Enter your location.")
            return
        with st.spinner("Finding providers..."):
            user_prompt = f"Find telemedicine/doctor appointment options for {specialty} in {location}."
            payload = {
                "contents": [{"parts": [{"text": user_prompt}]}],
                "tools": [{"google_search": {}}],
                "systemInstruction": {"parts": [
                    {"text": "Give local results and online options. Use markdown and cite sources."}
                ]}
            }
            response = google_api_call(
                model="gemini-2.5-flash-preview-05-20",
                endpoint="generateContent",
                payload=payload
            )
            if response and response.get('candidates'):
                st.write(response['candidates'][0]['content']['parts'][0]['text'])
            else:
                st.error("Doctor search failed.")


def emergency_support_page():
    st.header("Emergency Medical Support 🚨")
    st.write("Find nearby hospitals quickly in an emergency.")
    city = st.text_input("Enter city or area for emergency hospital search:")
    if st.button("Find Emergency Hospitals"):
        if not city:
            st.error("Enter a city/area.")
            return
        with st.spinner("Finding emergency hospitals..."):
            user_prompt = f"List major emergency hospitals and support options in {city}."
            payload = {
                "contents": [{"parts": [{"text": user_prompt}]}],
                "tools": [{"google_search": {}}],
                "systemInstruction": {"parts": [
                    {"text": "Reply with local hospital/emergency centers (address/contact). Use markdown."}
                ]}
            }
            response = google_api_call(
                model="gemini-2.5-flash-preview-05-20",
                endpoint="generateContent",
                payload=payload
            )
            if response and response.get('candidates'):
                st.write(response['candidates'][0]['content']['parts'][0]['text'])
            else:
                st.error("Search failed.")


# -------------------------- Sidebar History -------------------------

def show_history_sidebar():
    user_id = st.session_state.get('user_id')
    if not user_id:
        return
    st.sidebar.header("Your History")
    symptoms, mental = load_user_history(user_id)

    st.sidebar.subheader("Symptom Entries")
    for entry in symptoms[:5]:
        st.sidebar.markdown(f"**{entry['timestamp']}**")
        st.sidebar.markdown(f"Symptoms: {entry['symptoms']}")
        st.sidebar.markdown(f"Response: {entry['response'][:100]}...")
        st.sidebar.markdown("---")

    st.sidebar.subheader("Mental Health Entries")
    for entry in mental[:5]:
        st.sidebar.markdown(f"**{entry['timestamp']}**")
        st.sidebar.markdown(f"Note: {entry['mood_note']}")
        st.sidebar.markdown(f"Sentiment: {entry['sentiment']:.2f}")
        st.sidebar.markdown(f"Response: {entry['response'][:100]}...")
        st.sidebar.markdown("---")


# -------------------------- Main Navigation -------------------------

TOTAL_FEATURES = """
*Total Features:*
 1.⁠ ⁠Personal Details
 2.⁠ ⁠Health & Medicine (Symptom Checker)
 3.⁠ ⁠Wellness & Fitness (Exercise Routines)
 4.⁠ ⁠Nutrition & Diet (Diet Plans)
 5.⁠ ⁠Mental Health (Mood Tracking & Support)
 6.⁠ ⁠Telemedicine & Doctor Appointments
 7.⁠ ⁠Emergency Medical Support
"""

st.sidebar.title("Parmatma Menu 🥕")
st.sidebar.markdown(TOTAL_FEATURES)

pages = {
    "-- Personal Details --": home_page,
    "BMI Calculator": bmi_calculator_page,
    "Symptom Checker": symptom_checker_page,
    "Nutrition Coach & Diet": nutrition_coach_page,
    "Exercise Routines": exercise_routines_page,
    "Mental Health Support": mental_health_page,
    "Doctor Appointments": doctor_appointments_page,
    "Emergency Medical Support": emergency_support_page,
}

selection = st.sidebar.radio("Choose a feature:", list(pages.keys()))
pages[selection]()

show_history_sidebar()
