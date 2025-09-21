import streamlit as st
from supabase import create_client
import datetime
import requests
from textblob import TextBlob

# --- Setup your keys in .streamlit/secrets.toml ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Parmatma - Health & Wellness", page_icon="🧘‍♂️", layout="centered")

# -------- Helper functions ---------

def call_gemini_api(prompt, system_instruction=""):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GOOGLE_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()['candidates'][0]['content']['parts'][0]['text']

def save_record(table, data):
    response = supabase.table(table).insert(data).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]["id"]
    else:
        st.error(f"Failed to save data to {table}.")
        return None

def fetch_records(table, user_id, limit=None):
    query = supabase.table(table).select("*").eq("user_id", user_id).order("created_at", desc=True)
    if limit:
        query = query.limit(limit)
    response = query.execute()
    return response.data if response.data else []

def fetch_user(user_id):
    res = supabase.table("users").select("*").eq("id", user_id).single().execute()
    return res.data

def calculate_bmi(weight, height):
    if height <= 0 or weight <= 0:
        return 0, "Invalid", "Height and weight must be positive numbers."
    bmi = weight / ((height / 100) ** 2)
    if bmi < 18.5:
        return bmi, "Underweight", "Focus on nutrient-rich foods and consult a professional."
    elif bmi < 25:
        return bmi, "Normal", "Maintain balanced diet and regular exercise."
    elif bmi < 30:
        return bmi, "Overweight", "Consider balanced diet and increased activity."
    else:
        return bmi, "Obese", "Seek medical guidance for personalized care."

def generate_report(user, symptoms, mental, appointments):
    lines = [f"User: {user['name']} (Age {user['age']}, Gender: {user['gender']})"]
    lines.append(f"Height: {user['height']} cm | Weight: {user['weight']} kg\n")
    lines.append("Symptoms:")
    for s in symptoms[:10]:
        lines.append(f"{s['created_at']}: {s['symptoms']} → {s['response'][:100]}...")
    lines.append("\nMental Health Logs:")
    for m in mental[:10]:
        lines.append(f"{m['created_at']}: You: {m['user_text']} → Coach: {m['bot_response'][:100]}...")
    lines.append("\nAppointments:")
    for a in appointments[:10]:
        lines.append(f"{a['date']} {a['time']}: {a['specialty']} at {a['location']} ({a['status']})")
    return "\n".join(lines)

# -------- Pages ---------

def page_personal_details():
    st.header("Your Personal Details")
    with st.form("form_personal"):
        name = st.text_input("Name")
        age = st.number_input("Age", 5, 120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0)
        weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0)
        submitted = st.form_submit_button("Save")
    if submitted:
        if not name.strip():
            st.error("Name is required.")
        else:
            user_id = save_record("users", {
                "name": name, "age": age, "gender": gender,
                "height": height, "weight": weight,
                "created_at": datetime.datetime.utcnow().isoformat()
            })
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.user_info = {"name": name, "age": age, "gender": gender,
                                             "height": height, "weight": weight}
                st.success(f"Welcome {name}! Your details saved.")

def page_bmi_calculator():
    st.header("BMI Calculator")
    user = st.session_state.get("user_info")
    if not user:
        st.info("Enter personal details first.")
        return
    bmi, category, advice = calculate_bmi(user["weight"], user["height"])
    st.metric("BMI", f"{bmi:.2f}")
    st.write(f"Category: **{category}**")
    st.write(advice)

def page_nutrition_coach():
    st.header("Nutrition Coach")
    user = st.session_state.get("user_info")
    if not user:
        st.info("Enter personal details first.")
        return
    bmi, category, _ = calculate_bmi(user["weight"], user["height"])
    goal = ""
    if category == "Underweight":
        goal = "a weekly meal plan to gain healthy weight"
    elif category in ["Overweight", "Obese"]:
        goal = "a balanced weekly meal plan for fat loss"
    else:
        goal = st.text_input("Enter your nutrition goal", "balanced diet")
    if st.button("Get Nutrition Plan"):
        if not goal.strip():
            st.error("Please enter a goal.")
            return
        prompt = f"Create {goal}. Reply as professional nutritionist in markdown."
        result = call_gemini_api(prompt)
        st.markdown(result)

def page_exercise_routines():
    st.header("Exercise Routines")
    user = st.session_state.get("user_info")
    if not user:
        st.info("Enter personal details first.")
        return
    parts = st.multiselect("Select body parts", ["Arms", "Legs", "Core", "Back", "Chest", "Full Body"])
    goal = st.text_input("Fitness goal", "general fitness")
    if st.button("Generate Routine"):
        if not parts:
            st.error("Select at least one body part.")
            return
        prompt = f"Create 5 exercises for {', '.join(parts)} targeting a {user['gender']} with goal {goal}, include timers."
        result = call_gemini_api(prompt)
        st.markdown(result)

def page_symptom_checker():
    st.header("Symptom Checker")
    symptoms = st.text_area("Describe your symptoms")
    if st.button("Analyze Symptoms"):
        if not symptoms.strip():
            st.error("Please provide symptom details.")
            return
        # Replace with real medical API or AI symptom checker if available
        response = "Possible causes include common cold or flu. Consult a healthcare professional."
        st.write(response)
        user_id = st.session_state.get("user_id")
        if user_id:
            save_record("symptom_entries", {
                "user_id": user_id,
                "symptoms": symptoms,
                "response": response,
                "created_at": datetime.datetime.utcnow().isoformat()
            })

def page_mental_health_chat():
    st.header("Mental Health Chat")
    if "user_id" not in st.session_state:
        st.info("Please enter personal details first.")
        return
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    user_input = st.text_input("Talk to your supportive coach")
    if st.button("Send") and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        convo = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.chat_history[-6:])
        reply = call_gemini_api(convo, "You are a kind and supportive coach. Respond shortly and kindly.")
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        sentiment = TextBlob(user_input).sentiment.polarity
        save_record("mental_health_chats", {
            "user_id": st.session_state.user_id,
            "user_text": user_input,
            "bot_response": reply,
            "sentiment": sentiment,
            "created_at": datetime.datetime.utcnow().isoformat()
        })
    for msg in st.session_state.chat_history:
        who = "You" if msg["role"] == "user" else "Coach"
        st.markdown(f"**{who}:** {msg['content']}")

def page_doctor_appointments():
    st.header("Doctor Appointment Booking")
    if "user_id" not in st.session_state:
        st.info("Please enter personal details first.")
        return
    with st.form("appointment_form"):
        specialty = st.selectbox("Specialty", ["General", "Cardiologist", "Dermatologist", "Dentist", "Other"])
        location = st.text_input("Location (City)")
        date = st.date_input("Date")
        time_ = st.time_input("Time")
        submitted = st.form_submit_button("Book Appointment")
    if submitted:
        if not location.strip():
            st.error("Please provide a location.")
            return
        save_record("appointments", {
            "user_id": st.session_state.user_id,
            "specialty": specialty,
            "location": location,
            "date": str(date),
            "time": str(time_),
            "status": "Booked",
            "created_at": datetime.datetime.utcnow().isoformat(),
        })
        st.success("Appointment booked!")
        st.markdown("[Book via Practo](https://www.practo.com)")
        st.markdown("[Book via Zocdoc](https://www.zocdoc.com)")
        st.markdown("[Book via TopDoctors](https://www.topdoctors.com)")

def page_emergency_support():
    st.header("Emergency Support")
    city = st.text_input("Enter your city for emergency services:")
    if st.button("Find Emergency Hospitals"):
        if not city.strip():
            st.error("Please enter a valid city.")
            return
        st.info(f"Searching emergency hospitals near {city}... (Feature to be integrated)")

def show_history_sidebar():
    if "user_id" not in st.session_state:
        return
    user, symptoms, mental, appointments = get_user_history(st.session_state.user_id)
    st.sidebar.header(f"Your Health History - {user['name']}")
    st.sidebar.subheader("Recent Symptoms")
    for s in symptoms[:5]:
        st.sidebar.markdown(f"- {s['created_at']}: {s['symptoms'][:50]}...")
    st.sidebar.subheader("Mental Health Logs")
    for m in mental[:5]:
        st.sidebar.markdown(f"- {m['created_at']}: {m['user_text'][:50]}...")
    st.sidebar.subheader("Appointments")
    for a in appointments[:5]:
        st.sidebar.markdown(f"- {a['date']} {a['time']} | {a['specialty']} at {a['location']} ({a['status']})")

    report_text = generate_report(user, symptoms, mental, appointments)
    st.sidebar.download_button("Download Full Health Report", report_text, "health_report.txt")

# -------- Navigation ----------

pages = {
    "Personal Details": page_personal_details,
    "BMI Calculator": page_bmi_calculator,
    "Nutrition Coach": page_nutrition_coach,
    "Exercise Routines": page_exercise_routines,
    "Symptom Checker": page_symptom_checker,
    "Mental Health Chat": page_mental_health_chat,
    "Doctor Appointments": page_doctor_appointments,
    "Emergency Support": page_emergency_support,
}

st.sidebar.title("Parmatma Menu")
choice = st.sidebar.radio("Select Feature", list(pages.keys()))
pages[choice]()
show_history_sidebar()
