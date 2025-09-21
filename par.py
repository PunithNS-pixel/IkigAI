import streamlit as st
import datetime
import pandas as pd
import requests
import time

st.set_page_config(
    page_title="Parmatma - Health & Wellness Tracker",
    page_icon="🧘‍♂️",
    layout="centered"
)

# --- Helper Functions ---
def google_api_call(model, endpoint, payload):
    api_key = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else ""
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:{endpoint}?key={api_key}"
    retries, max_retries, delay = 0, 3, 1
    while retries < max_retries:
        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            if response.status_code == 429:
                retries += 1; time.sleep(delay); delay *= 2
            else: raise err
        except Exception as e: raise e
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

# ----------------------------- Features -----------------------------

def home_page():
    st.title("Welcome to Parmatma 🧘‍♂️")
    st.markdown("Your all-in-one health and wellness companion.")
    with st.container(border=True):
        st.subheader("Personal Details")
        with st.form("personal_details_form"):
            name = st.text_input("Name")
            col1, col2 = st.columns(2)
            with col1: age = st.number_input("Age", min_value=5, max_value=120, step=1)
            with col2: gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, format="%.2f")
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, format="%.2f")
            submitted = st.form_submit_button("Submit Details")
            if submitted:
                if not name: st.error("Please enter your name.")
                elif height <= 0 or weight <= 0: st.error("Height and weight must be positive.")
                else:
                    st.session_state['personal'] = {
                        'name': name, 'age': age, 'gender': gender,
                        'height': height, 'weight': weight
                    }
                    bmi, category, advice = calculate_bmi_and_category(weight, height)
                    st.session_state['bmi_category'] = category
                    st.success(f"Hello {name}! Details saved. You can now use all features.")

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
    goal = st.text_input("Your nutrition/diet goal:",
        placeholder="e.g., 'Weekly meal plan for fat loss.'")
    if st.button("Get Nutrition Plan"):
        if not goal: st.error("Please enter your goal."); return
        with st.spinner("Preparing plan..."):
            user_prompt = f"Nutrition plan for: {goal}. Detailed, safe, actionable advice with sources."
            payload = {
                "contents": [{"parts": [{"text": user_prompt}]}],
                "tools": [{"google_search": {}}],
                "systemInstruction": {"parts": [
                    {"text": "Reply as a professional nutritionist. Use markdown and cite sources."}
                ]}
            }
            response = google_api_call(
                model="gemini-2.5-flash-preview-05-20",
                endpoint="generateContent",
                payload=payload
            )
            if response and response.get('candidates'):
                generated_text = response['candidates'][0]['content']['parts'][0]['text']
                sources = response['candidates'][0].get('groundingMetadata', {}).get('groundingAttributions', [])
                st.subheader("Your Nutrition Plan")
                st.write(generated_text)
                if sources:
                    st.subheader("Sources")
                    for i, s in enumerate(sources):
                        if 'web' in s and 'title' in s['web'] and 'uri' in s['web']:
                            st.markdown(f"*{i+1}.* [{s['web']['title']}]({s['web']['uri']})")
            else:
                st.error("Failed to generate nutrition plan.")

def exercise_routines_page():
    st.header("Exercise Routines & Fitness Plans 🏃")
    fitness_goal = st.text_input("Your fitness goal:",
        placeholder="e.g., 'Strength training routine for beginners.'")
    if st.button("Get Exercise Routine"):
        if not fitness_goal: st.error("Enter your fitness goal."); return
        with st.spinner("Generating exercise plan..."):
            user_prompt = f"Create an exercise routine for: {fitness_goal}."
            payload = {
                "contents": [{"parts": [{"text": user_prompt}]}],
                "systemInstruction": {"parts": [
                    {"text": "Reply as a professional trainer. Use markdown format."}
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
                st.error("Failed to generate routine.")

def symptom_checker_page():
    st.header("Symptom Checker 🩺")
    symptoms = st.text_area("Describe your symptoms:",
        placeholder="e.g., 'I have fever, headache and cough.'")
    if st.button("Analyze Symptoms"):
        if not symptoms: st.error("Please describe your symptoms."); return
        with st.spinner("Analyzing..."):
            user_prompt = (f"Symptoms: {symptoms}. Give potential causes, guidance (not diagnosis), "
                           "and urgency advice. Always recommend a doctor's visit for serious conditions.")
            payload = {
                "contents": [{"parts": [{"text": user_prompt}]}],
                "tools": [{"google_search": {}}],
                "systemInstruction": {
                    "parts": [
                        {"text": "Act as a medical assistant. Do not diagnose. Use markdown and cite sources."}
                    ]
                }
            }
            response = google_api_call(
                model="gemini-2.5-flash-preview-05-20",
                endpoint="generateContent",
                payload=payload
            )
            if response and response.get('candidates'):
                text = response['candidates'][0]['content']['parts'][0]['text']
                sources = response['candidates'][0].get('groundingMetadata', {}).get('groundingAttributions', [])
                st.write(text)
                if sources:
                    st.subheader("Sources")
                    for i, s in enumerate(sources):
                        if 'web' in s and 'title' in s['web'] and 'uri' in s['web']:
                            st.markdown(f"*{i+1}.* [{s['web']['title']}]({s['web']['uri']})")
            else:
                st.error("Failed to analyze symptoms.")

def mental_health_page():
    st.header("Mental Health Support ❤️‍🩹")
    st.write("Track your mood and get support. Not a substitute for professional help.")
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = []
    with st.container(border=True):
        st.markdown("### New Entry")
        with st.form("journal_entry_form"):
            mood = st.selectbox("Your mood today?", ["😊 Great", "🙂 Good", "😐 Okay", "🙁 Down", "😔 Sad"])
            note = st.text_area("Quick thought (optional)")
            submitted = st.form_submit_button("Save & Get Advice")
            if submitted:
                entry = {'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), 'mood': mood, 'note': note}
                st.session_state.journal_entries.append(entry)
                with st.spinner("Getting advice..."):
                    user_prompt = f"Mood: {mood}. Note: '{note}'. Provide supportive advice."
                    payload = {
                        "contents": [{"parts": [{"text": user_prompt}]}],
                        "systemInstruction": {"parts": [
                            {"text": "Act as a kind, supportive coach. Include disclaimer."}
                        ]}
                    }
                    response = google_api_call(
                        model="gemini-2.5-flash-preview-05-20",
                        endpoint="generateContent",
                        payload=payload
                    )
                    if response and response.get('candidates'):
                        st.success("Entry saved!")
                        st.markdown("---")
                        st.subheader("Support & Advice")
                        st.write(response['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.error("Failed to generate advice.")
                st.experimental_rerun()
    st.markdown("---")
    st.subheader("Mood Trends")
    if st.session_state.journal_entries:
        df_entries = pd.DataFrame(st.session_state.journal_entries)
        df_entries['mood_label'] = df_entries['mood'].apply(lambda x: x.split()[0])
        st.bar_chart(df_entries['mood_label'].value_counts())
        st.markdown("### Past Entries")
        for entry in reversed(st.session_state.journal_entries):
            with st.expander(f"*{entry['date']} - {entry['mood']}*"):
                st.write(f"*Note:* {entry['note']}")
    else:
        st.info("No entries yet.")

def doctor_appointments_page():
    st.header("Doctor Appointments & Telemedicine 🏥")
    st.write("Use symptom checker, get advice, and book appointments.")
    location = st.text_input("Your city or locality for nearby doctors:")
    specialty = st.selectbox("Specialty", ["General", "Cardiologist", "Dermatologist", "Dentist", "Other"])
    if st.button("Find Nearby Doctor"):
        if not location: st.error("Enter your location."); return
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
        if not city: st.error("Enter a city/area."); return
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
 8.⁠ ⁠Symptom Analysis
 9.⁠ ⁠Diet Plans
10.⁠ ⁠Exercise Routines
11.⁠ ⁠Mental Health Support
12.⁠ ⁠Finding Nearby Hospitals
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