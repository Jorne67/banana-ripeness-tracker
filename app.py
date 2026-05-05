import streamlit as st
from PIL import Image
import numpy as np
import keras
import datetime

st.set_page_config(page_title="🍌 Banana Ripeness Tracker", layout="centered")
st.title("🍌 Banana Ripeness Tracker")
st.markdown("Lade ein Foto deiner Banane hoch und die App bestimmt den Reifegrad.")

RIPENESS_LABELS = {
    0: "🟢 Stufe 1 – Grün",
    1: "🟡🟢 Stufe 2 – Mehr grün als gelb",
    2: "🟡🟢 Stufe 3 – Mehr gelb als grün",
    3: "🟡 Stufe 4 – Gelb mit grünen Spitzen ⭐ Optimal",
    4: "🟡 Stufe 5 – Vollgelb",
    5: "🟡🟤 Stufe 6 – Vollgelb mit braunen Punkten",
    6: "🟤 Stufe 7 – Braun",
}

DAYS_TO_OPTIMAL = {
    0: 7,
    1: 5,
    2: 2,
    3: 0,
    4: -1,
    5: -2,
    6: -4,
}

def stage_to_buy_for_day(days_from_now):
    best = min(DAYS_TO_OPTIMAL.items(), key=lambda x: abs(x[1] - days_from_now))
    return best[0]

@st.cache_resource
def load_model():
    model = keras.models.load_model("model/keras_model.h5", compile=False)
    return model

model = load_model()

def predict_ripeness(image):
    img = image.resize((224, 224))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    predictions = model.predict(img_array)
    class_index = np.argmax(predictions[0])
    confidence = predictions[0][class_index]
    return class_index, confidence

if "bananas" not in st.session_state:
    st.session_state.bananas = []

# --- UPLOAD ---
st.divider()
st.subheader("📸 Banane hochladen")
uploaded_file = st.file_uploader("Foto der Banane", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Deine Banane", width=300)

    with st.spinner("🔍 Analyse läuft..."):
        class_index, confidence = predict_ripeness(image)

    st.divider()
    st.subheader("📊 Ergebnis")
    st.success(f"**Erkannter Reifegrad:** {RIPENESS_LABELS[class_index]}")
    st.write(f"Konfidenz: {confidence:.0%}")

    days = DAYS_TO_OPTIMAL[class_index]
    today = datetime.date.today()

    if days == 0:
        st.success("✅ Diese Banane ist **heute** perfekt!")
    elif days > 0:
        optimal_date = today + datetime.timedelta(days=days)
        st.info(f"📆 Perfekt am: **{optimal_date.strftime('%A, %d.%m.%Y')}** (in {days} Tagen)")
    else:
        st.warning(f"⚠️ Der optimale Zeitpunkt war vor {abs(days)} Tag(en) – Banane ist überreif.")

    if st.button("✅ Banane speichern"):
        st.session_state.bananas.append(class_index)
        st.success("Banane gespeichert!")

# --- KALENDER ---
st.divider()
st.subheader("📅 Kalender – Nächste 7 Tage")

if st.session_state.bananas:
    today = datetime.date.today()
    covered = set()
    for ci in st.session_state.bananas:
        d = today + datetime.timedelta(days=DAYS_TO_OPTIMAL[ci])
        if d >= today:
            covered.add(d)

    cols = st.columns(7)
    for i, col in enumerate(cols):
        day = today + datetime.timedelta(days=i)
        if day in covered:
            col.markdown(f"""<div style='background-color:#2ecc71;padding:10px;border-radius:8px;text-align:center;color:white;'><b>{day.strftime('%a')}</b><br>{day.strftime('%d.%m')}<br>🍌</div>""", unsafe_allow_html=True)
        else:
            col.markdown(f"""<div style='background-color:#e74c3c;padding:10px;border-radius:8px;text-align:center;color:white;'><b>{day.strftime('%a')}</b><br>{day.strftime('%d.%m')}<br>❌</div>""", unsafe_allow_html=True)

    # --- EINKAUFSEMPFEHLUNG ---
    st.divider()
    st.subheader("🛒 Einkaufsempfehlung")

    red_days = [i for i in range(7) if today + datetime.timedelta(days=i) not in covered]

    if not red_days:
        st.success("👍 Du bist perfekt versorgt für die nächsten 7 Tage – kein Nachkauf nötig!")
    else:
        nearest_red = min(red_days)
