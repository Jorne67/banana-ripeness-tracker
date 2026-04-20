import streamlit as st
from PIL import Image
import datetime

st.set_page_config(page_title="🍌 Banana Ripeness Tracker", layout="centered")

st.title("🍌 Banana Ripeness Tracker")
st.markdown("Lade ein Foto deiner Banane hoch und die App bestimmt den Reifegrad.")

# Reifegrad-Skala
RIPENESS_LABELS = {
    1: "🟢 Grün",
    2: "🟡🟢 Mehr grün als gelb",
    3: "🟡🟢 Mehr gelb als grün",
    4: "🟡 Gelb mit grünen Spitzen",
    5: "🟡 Vollgelb",
    6: "🟡🟤 Vollgelb mit braunen Punkten",
    7: "🟤 Braun",
}
OPTIMAL_STAGE = 4

st.divider()
st.subheader("📸 Banane hochladen")
uploaded_file = st.file_uploader("Foto der Banane", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Deine Banane", width=300)
    st.info("🔍 KI-Analyse folgt in den nächsten Schritten...")
