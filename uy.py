import streamlit as st
import datetime
import requests
import time
from textblob import TextBlob
import folium
from streamlit_folium import st_folium


st.set_page_config(page_title="Parmatma - Health & Wellness", page_icon="🧘", layout="centered")


# ----- Helper functions -----


def google_api_call(model, endpoint, prompt, system_instruction=None):
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key:
        st.error("Missing Google API key!")
        st.stop()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:{endpoint}?key={api_key}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    if system_instruction:
        data["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    resp = requests.post(url, json=data)
    if resp.status_code == 429:
        time.sleep(2)
        resp = requests.post(url, json=data)
    if not resp.ok:
        st.error(f"Google API error {resp.status_code}: {resp.text}")
        st.stop()
    return resp.json()


def calculate_bmi(weight_kg, height_cm):
    if weight_kg <= 0 or height_cm <= 0:
        return 0, "Invalid", "Height and weight must be positive."
    bmi = weight_kg / ((height_cm / 100) ** 2)
    if bmi < 18.5:
        return bmi, "Underweight", "Focus on nutrient-dense foods and gain weight healthily."
    elif bmi < 25:
        return bmi, "Normal", "Maintain your current healthy lifestyle."
    elif bmi < 30:
        return bmi, "Overweight", "Consider a balanced diet and exercise."
    else:
        return bmi, "Obese", "Consult a healthcare provider."


def get_platforms_by_location(city):
    city = city.strip().lower()
    metro_platforms = {
        "mumbai": [
            ("Practo", "https://www.practo.com", "Mobile-friendly, video & clinic consults"),
            ("Apollo 24|7", "https://www.apollo247.com", "Telehealth + medicine delivery"),
            ("MFine", "https://www.mfine.co", "AI-driven video consults"),
        ],
        "bangalore": [
            ("Practo", "https://www.practo.com/bangalore", "Top Bangalore doctors"),
            ("MFine", "https://www.mfine.co", "Teleconsult & fast support"),
            ("DocPrime", "https://www.docprime.com", "24/7 video consults"),
        ],
        "delhi": [
            ("Practo", "https://www.practo.com/delhi", "Delhi doctors with instant booking"),
            ("Apollo 24|7", "https://www.apollo247.com", "Full hospital network support"),
            ("1mg", "https://www.1mg.com", "Teleconsult & delivery"),
        ]
    }
    return metro_platforms.get(city, [
        ("Practo", "https://www.practo.com", "Instant booking"),
        ("Apollo 24|7", "https://www.apollo247.com", "Online consults"),
        ("MFine", "https://www.mfine.co", "Quick video calls"),
        ("1mg", "https://www.1mg.com", "Consult & medicine delivery"),
        ("DocPrime", "https://www.docprime.com", "Video consultations"),
    ])


def geocode_location(location):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "ParmatmaHealthApp/1.0 (+https://yourdomain.com/contact)"
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        result = response.json()[0]
        return float(result["lat"]), float(result["lon"])
    else:
        return None, None


def get_nearby_hospitals(lat, lon, radius=5000):
    overpass_query = f"""
    [out:json];
    node["amenity"="hospital"](around:{radius},{lat},{lon});
    out body;
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    response = requests.post(overpass_url, data={"data": overpass_query})
    if response.status_code == 200:
        data = response.json()
        hospitals = []
        for element in data.get("elements", []):
            name = element.get("tags", {}).get("name", "Unnamed Hospital")
            hospital_lat = element.get("lat")
            hospital_lon = element.get("lon")
            hospitals.append({
                "name": name,
                "lat": hospital_lat,
                "lon": hospital_lon
            })
        return hospitals
    else:
        return []


def display_hospitals_map(hospitals, center_lat, center_lon):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    for hos in hospitals:
        folium.Marker(
            [hos['lat'], hos['lon']],
            popup=hos['name']
        ).add_to(m)
    st_folium(m, width=700, height=450)


def home():
    st.title("Welcome to Parmatma 🧘")
    with st.form("profile_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", 5, 120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        height = st.number_input("Height (cm)", 100, 250)
        weight = st.number_input("Weight (kg)", 20, 200)
        submitted = st.form_submit_button("Save Profile")
    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
        else:
            st.session_state.profile = dict(name=name, age=age, gender=gender, height=height, weight=weight)
            bmi, category, advice = calculate_bmi(weight, height)
            st.session_state.bmi_category = category
            st.success(f"Profile saved! BMI: {bmi:.2f} ({category}). {advice}")


def bmi_calculator():
    st.header("BMI Calculator")
    profile = st.session_state.get("profile")
    if not profile:
        st.info("Please fill your profile first.")
        return
    bmi, category, advice = calculate_bmi(profile["weight"], profile["height"])
    st.metric("BMI", f"{bmi:.2f}")
    st.write(f"Category: *{category}*")
    st.write(advice)


def nutrition_coach():
    st.header("Nutrition Coach")
    profile = st.session_state.get("profile")
    if not profile:
        st.info("Please fill your profile first.")
        return
    category = st.session_state.get("bmi_category", "Unknown")
    st.write(f"Detected BMI Category: {category}")
    # Additional nutrition coach logic here...


def exercise_routines():
    st.header("Exercise Routines")
    profile = st.session_state.get("profile")
    if not profile:
        st.info("Please provide your profile details on the Home page first.")
        return
    # Additional exercise routines logic here...


def symptom_checker():
    st.header("Symptom Checker")
    symptoms = st.text_area("Describe your symptoms")
    if st.button("Analyze"):
        if not symptoms.strip():
            st.error("Please enter symptoms.")
            return
        prompt = (
            f"User symptoms: {symptoms}. "
            "Predict possible diseases or conditions matching these symptoms. "
            "For each, provide a confidence score as a percentage and list which symptoms matched. "
            "Give only the top 3 predictions in a clear, brief format."
        )
        response = google_api_call("gemini-2.0-flash-001", "generateContent", prompt)
        candidates = response.get("candidates", [])
        if candidates:
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            st.markdown(text)
        else:
            st.error("No response from symptom checker API.")


def mental_health_chat():
    st.header("Mental Health Support Chat")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    user_input = st.text_input("Talk to your wellness coach")
    send_clicked = st.button("Send")
    if send_clicked and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        convo = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.chat_history[-5:])
        reply = google_api_call("gemini-2.0-flash-001", "generateContent", convo, "Short, kind, supportive replies under 100 words.")
        candidates = reply.get("candidates", [])
        if candidates:
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "I'm here to help.")
        else:
            text = "I'm here to help."
        st.session_state.chat_history.append({"role": "assistant", "content": text})
        sentiment = TextBlob(user_input).sentiment.polarity
        emotion = "Positive" if sentiment > 0.2 else "Neutral" if sentiment > -0.2 else "Negative"
        st.markdown(f"Sentiment score: *{sentiment:.2f}* ({emotion})")
        if emotion == "Negative":
            st.info("Feeling down? Take a short break, breathe deeply, or reach out to someone you trust.")
        elif emotion == "Positive":
            st.info("Glad to hear you're feeling good! Keep up the positive mindset.")
        else:
            st.info("Thanks for sharing. Remember, support is available whenever you need it.")
    for msg in st.session_state.chat_history:
        who = "You" if msg["role"] == "user" else "Coach"
        st.markdown(f"{who}:** {msg['content']}")


def doctor_appointments():
    st.header("Doctor Appointment Booking")
    city = st.text_input("Enter your city or area")
    specialty = st.selectbox("Select Specialization", ["General Physician", "Cardiologist", "Dermatologist", "Pediatrician", "Gynecologist", "Other"])
    if st.button("Show Platforms"):
        if not city.strip():
            st.error("Enter a valid city or area.")
            return
        platforms = get_platforms_by_location(city)
        st.info(f"Trusted online platforms for {specialty}s near {city.title()}:")
        for name, url, desc in platforms:
            st.markdown(f"[{name}]({url}) — {desc}")


def emergency_support():
    st.title("Parmatma Emergency Support")
    st.write("Find hospitals near your location based on OpenStreetMap data.")
    location = st.text_input("Enter your city or address")
    if st.button("Find Hospitals"):
        if not location.strip():
            st.error("Please enter a valid location.")
        else:
            lat, lon = geocode_location(location)
            if lat is None or lon is None:
                st.error("Failed to find coordinates for the location. Please try another location.")
            else:
                st.success(f"Location found: Latitude {lat:.5f}, Longitude {lon:.5f}")
                hospitals = get_nearby_hospitals(lat, lon)
                if hospitals:
                    st.success(f"Found {len(hospitals)} hospitals within 5 km of {location}:")
                    for hos in hospitals[:10]:
                        st.write(f"- **{hos['name']}** (Lat: {hos['lat']:.5f}, Lon: {hos['lon']:.5f})")
                    display_hospitals_map(hospitals, lat, lon)
                else:
                    st.warning(f"No hospitals found within 5 km of {location}.")


# ------ Sidebar Navigation -----


st.sidebar.title("Parmatma Features")
page = st.sidebar.radio("Choose a feature", [
    "Home",
    "BMI Calculator",
    "Nutrition Coach",
    "Exercise Routines",
    "Symptom Checker",
    "Mental Health Support",
    "Doctor Appointment Booking",
    "Emergency Support"
])


# ------ Page switcher ------
if page == "Home":
    home()
elif page == "BMI Calculator":
    bmi_calculator()
elif page == "Nutrition Coach":
    nutrition_coach()
elif page == "Exercise Routines":
    exercise_routines()
elif page == "Symptom Checker":
    symptom_checker()
elif page == "Mental Health Support":
    mental_health_chat()
elif page == "Doctor Appointment Booking":
    doctor_appointments()
elif page == "Emergency Support":
    emergency_support()