import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import json
import paho.mqtt.client as paho
from gtts import gTTS
from googletrans import Translator


# ==== FUNCIONES MQTT ====
def on_publish(client, userdata, result):
    print("✅ El dato ha sido publicado\n")
    pass


def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(f"📩 Mensaje recibido: {message_received}")


# ==== CONFIGURACIÓN MQTT ====
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBpapuuu")
client1.on_message = on_message


# ==== CONFIGURACIÓN DE PÁGINA ====
st.set_page_config(page_title="Control por Voz", page_icon="🎙️")

# ==== ESTILOS (SOLO VISUAL) ====
st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at top left, #141726, #27293a);
            color: #F5F5F5;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        .main-card {
            background: rgba(15, 15, 30, 0.96);
            border-radius: 24px;
            padding: 2.3rem 2.6rem;
            box-shadow: 0 22px 50px rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin-top: 2.5rem;
        }

        .app-title {
            font-size: 2.4rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            margin-bottom: 0.2rem;
        }

        .app-subtitle {
            font-size: 1.1rem;
            font-weight: 600;
            opacity: 0.9;
            margin-bottom: 1rem;
        }

        .helper-text {
            font-size: 0.9rem;
            opacity: 0.82;
        }

        .voice-card {
            margin-top: 1.5rem;
            padding: 1.2rem 1.5rem;
            border-radius: 18px;
            background: linear-gradient(120deg, rgba(33,150,243,0.18), rgba(156,39,176,0.18));
            border: 1px solid rgba(255,255,255,0.09);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==== LAYOUT PRINCIPAL (ORGANIZA LA VISTA) ====
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        image = Image.open("Voz.png")
        st.image(image, width=200)

    with col2:
        st.markdown('<div class="app-title">🎙️ INTERFACES MULTIMODALES</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-subtitle">CONTROL POR VOZ</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="helper-text">Toca el botón y habla cerca del micrófono. '
            'El texto se reconocerá, se enviará por MQTT y se reproducirá por voz.</div>',
            unsafe_allow_html=True,
        )

    # ==== BOTÓN DE ESCUCHA ====  (LÓGICA ORIGINAL)
    st.markdown('<div class="voice-card">', unsafe_allow_html=True)
    st.write("Toca el botón y habla...")

    stt_button = Button(label="🎤 Iniciar reconocimiento", width=250)

    stt_button.js_on_event(
        "button_click",
        CustomJS(
            code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "es-ES";
     
        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if (value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
    """
        ),
    )

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0,
    )

    # ==== PROCESAMIENTO DE RESULTADO ====  (LÓGICA ORIGINAL)
    if result and "GET_TEXT" in result:

        with st.spinner("🎧 Escuchando y procesando..."):
            time.sleep(1.5)

        # Texto reconocido
        text = result.get("GET_TEXT").strip()
        st.success(f"🗣️ Texto reconocido: {text}")

        # Traducir texto
        translator = Translator()
        translated = translator.translate(text, dest="es").text
        st.info(f"🔤 Traducción: {translated}")

        # Publicar mensaje en MQTT
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": text})
        client1.publish("ZuluMikerCasa", message)

        # Crear carpeta temporal si no existe
        os.makedirs("temp", exist_ok=True)

        # Reproducir voz de respuesta
        tts = gTTS(f"Dijiste: {translated}", lang="es")
        tts.save("temp/voice.mp3")
        st.audio("temp/voice.mp3", format="audio/mp3")

    st.markdown("</div>", unsafe_allow_html=True)  # cierre main-card
