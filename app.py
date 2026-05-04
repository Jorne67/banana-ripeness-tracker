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

DAYS_TO_RIPEN = {0: 5, 1: 4, 2: 3, 3: 0, 4: -1, 5: -2, 6: -3}
OPTIMAL_STAGE = 3

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

def get_covered_days(bananas):
    """Gibt eine Liste von Datum-Strings zurück, die durch Bananen abgedeckt sind."""
    covered = set()
    today = datetime.date.today()
    for class_index in bananas:
        days = DAYS_TO_RIPEN[class_index]
        optimal_date = today + datetime.timedelta(days=days)
        if optimal_date >= today:
            covered.add(optimal_date)
    return covered

# Session State für gespeicherte Bananen
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

    days = DAYS_TO_RIPEN[class_index]
    today = datetime.date.today()

    if days == 0:
        st.success("✅ Diese Banane ist **heute** perfekt!")
    elif days > 0:
        optimal_date = today + datetime.timedelta(days=days)
        st.info(f"📆 Perfekt am: **{optimal_date.strftime('%A, %d.%m.%Y')}** (in {days} Tagen)")
    else:
        st.warning("⚠️ Diese Banane ist bereits über den optimalen Zeitpunkt hinaus.")

    if st.button("✅ Banane speichern"):
        st.session_state.bananas.append(class_index)
        st.success("Banane gespeichert!")

# --- KALENDER ---
st.divider()
st.subheader("📅 Kalender – Nächste 7 Tage")

if st.session_state.bananas:
    covered_days = get_covered_days(st.session_state.bananas)
    today = datetime.date.today()

    cols = st.columns(7)
    for i, col in enumerate(cols):
        day = today + datetime.timedelta(days=i)
        day_name = day.strftime("%a")
        day_str = day.strftime("%d.%m")
        if day in covered_days:
            col.markdown(f"""
                <div style='background-color:#2ecc71;padding:10px;border-radius:8px;text-align:center;color:white;'>
                <b>{day_name}</b><br>{day_str}<br>🍌
                </div>""", unsafe_allow_html=True)
        else:
            col.markdown(f"""
                <div style='background-color:#e74c3c;padding:10px;border-radius:8px;text-align:center;color:white;'>
                <b>{day_name}</b><br>{day_str}<br>❌
                </div>""", unsafe_allow_html=True)

    # --- EINKAUFSEMPFEHLUNG ---
    st.divider()
    st.subheader("🛒 Einkaufsempfehlung")

    red_days = []
    for i in range(7):
        day = today + datetime.timedelta(days=i)
        if day not in covered_days:
            red_days.append(i)

    if not red_days:
        st.success("👍 Du bist perfekt versorgt – kein Nachkauf nötig!")
    else:
        furthest_red = max(red_days)
        needed_stage = None
        for stage, days_offset in DAYS_TO_RIPEN.items():
            if days_offset == furthest_red:
                needed_stage = stage
                break
        if needed_stage is None:
            needed_stage = max(0, min(6, furthest_red - 1))

        st.warning(f"⚠️ Du hast **{len(red_days)} Tag(e)** ohne passende Banane!")
        st.info(f"👉 Kauf heute eine Banane in **{RIPENESS_LABELS[needed_stage]}**, um alle Lücken zu füllen.")

    if st.button("🗑️ Alle Bananen zurücksetzen"):
        st.session_state.bananas = []
        st.rerun()

else:
    st.info("📭 Noch keine Bananen gespeichert. Lade ein Foto hoch und speichere deine Bananen!")
