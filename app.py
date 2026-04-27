import streamlit as st
from PIL import Image
import numpy as np
import tf_keras as tf
import datetime

st.set_page_config(page_title="🍌 Banana Ripeness Tracker", layout="centered")

st.title("🍌 Banana Ripeness Tracker")
st.markdown("Lade ein Foto deiner Banane hoch und die App bestimmt den Reifegrad.")

# Reifegrad-Skala
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

# Modell laden
@st.cache_resource
def load_model():
    model = tf.keras.models.load_model("model/keras_model.h5", compile=False)
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
    
    st.divider()
    st.subheader("📅 Kalender")
    if days == 0:
        st.success("✅ Diese Banane ist **heute** perfekt!")
    elif days > 0:
        optimal_date = today + datetime.timedelta(days=days)
        st.info(f"📆 Perfekt am: **{optimal_date.strftime('%A, %d.%m.%Y')}** (in {days} Tagen)")
    else:
        st.warning("⚠️ Diese Banane ist bereits über den optimalen Zeitpunkt hinaus.")

    st.divider()
    st.subheader("🛒 Einkaufsempfehlung")
    if days <= 1:
        st.warning("👉 Kauf eine Banane der **Stufe 1–2** nach, damit du in 4–5 Tagen wieder eine perfekte hast!")
    else:
        st.success("👍 Du bist gut versorgt – kein Nachkauf nötig!")
