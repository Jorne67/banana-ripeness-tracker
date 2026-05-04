import streamlit as st
from PIL import Image
import numpy as np
import datetime
from ultralytics import YOLO

st.set_page_config(page_title="🍌 Banana Tracker – YOLOv8", layout="centered")
st.title("🍌 Banana Ripeness Tracker – YOLOv8")
st.markdown("Säule A: Vortrainiertes YOLOv8 Modell zur Bananenerkennung + Farb-Analyse")

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

@st.cache_resource
def load_yolo():
    return YOLO("yolov8n.pt")

model = load_yolo()

def analyze_color(image, box):
    """Analysiert die Farbe der Banane innerhalb der Bounding Box."""
    x1, y1, x2, y2 = map(int, box)
    crop = np.array(image.crop((x1, y1, x2, y2)))
    r = crop[:,:,0].mean()
    g = crop[:,:,1].mean()
    b = crop[:,:,2].mean()

    if g > r and g > b:
        return 0  # Grün
    elif r > 200 and g > 200 and b < 100:
        return 4  # Vollgelb
    elif r > 180 and g > 160 and b < 80:
        return 3  # Gelb mit grünen Spitzen
    elif r > 150 and g > 130 and b < 80:
        return 2  # Mehr gelb als grün
    elif r > 120 and g > 100 and b < 70:
        return 1  # Mehr grün als gelb
    elif b > 80 and r > 150:
        return 5  # Braune Punkte
    else:
        return 6  # Braun

if "bananas_yolo" not in st.session_state:
    st.session_state.bananas_yolo = []

st.divider()
st.subheader("📸 Banane hochladen")
uploaded_file = st.file_uploader("Foto der Banane", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Deine Banane", width=300)

    with st.spinner("🔍 YOLOv8 analysiert..."):
        results = model(np.array(image))
        banana_boxes = []
        for result in results:
            for box in result.boxes:
                if result.names[int(box.cls)] == "banana":
                    banana_boxes.append(box.xyxy[0].tolist())

    st.divider()
    st.subheader("📊 Ergebnis")

    if not banana_boxes:
        st.error("❌ Keine Banane erkannt! Bitte ein deutlicheres Foto hochladen.")
    else:
        st.success(f"✅ {len(banana_boxes)} Banane(n) erkannt!")
        box = banana_boxes[0]
        class_index = analyze_color(image, box)
        st.success(f"**Erkannter Reifegrad:** {RIPENESS_LABELS[class_index]}")

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
            st.session_state.bananas_yolo.append(class_index)
            st.success("Banane gespeichert!")

if st.session_state.bananas_yolo:
    st.divider()
    st.subheader("📅 Kalender – Nächste 7 Tage")
    today = datetime.date.today()
    covered = set()
    for ci in st.session_state.bananas_yolo:
        d = today + datetime.timedelta(days=DAYS_TO_RIPEN[ci])
        if d >= today:
            covered.add(d)

    cols = st.columns(7)
    for i, col in enumerate(cols):
        day = today + datetime.timedelta(days=i)
        if day in covered:
            col.markdown(f"""<div style='background-color:#2ecc71;padding:10px;border-radius:8px;text-align:center;color:white;'><b>{day.strftime('%a')}</b><br>{day.strftime('%d.%m')}<br>🍌</div>""", unsafe_allow_html=True)
        else:
            col.markdown(f"""<div style='background-color:#e74c3c;padding:10px;border-radius:8px;text-align:center;color:white;'><b>{day.strftime('%a')}</b><br>{day.strftime('%d.%m')}<br>❌</div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("🛒 Einkaufsempfehlung")
    red_days = [i for i in range(7) if today + datetime.timedelta(days=i) not in covered]
    if not red_days:
        st.success("👍 Du bist perfekt versorgt!")
    else:
        furthest = max(red_days)
        needed = min(furthest, 6)
        st.warning(f"⚠️ {len(red_days)} Tag(e) ohne Banane!")
        st.info(f"👉 Kauf heute eine Banane in **{RIPENESS_LABELS[needed]}**")

    if st.button("🗑️ Zurücksetzen"):
        st.session_state.bananas_yolo = []
        st.rerun()
