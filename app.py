import os
import time
import json

import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import paho.mqtt.client as paho
from gtts import gTTS
from googletrans import Translator


# ====================== FUNCIONES MQTT ======================
def on_publish(client, userdata, result):
    print("✅ El dato ha sido publicado\n")
    pass


def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(f"📩 Mensaje recibido: {message_received}")


# ====================== CONFIGURACIÓN MQTT ======================
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBpapuuu")
client1.on_message = on_message


# ====================== CONFIGURACIÓN DE PÁGINA ======================
st.set_page_config(
    page_title="Control por Voz",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------- ESTILOS PERSONALIZADOS (CSS) ----------
st.markdown(
    """
    <style>
        /* Fondo general */
        .stApp {
            background: radial-gradient(circle at top left, #1f1c2c, #928dab);
            color: #F5F5F5;
        }

        /* Esconder menú y footer de Streamlit si quieres más “app feeling” */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Contenedor principal tipo card */
        .main-card {
            background: rgba(15, 15, 30, 0.92);
            border-radius: 20px;
            padding: 2rem 2.5rem;
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.55);
            border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .title-text {
            font-size: 2.3rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            margin-bottom: 0.3rem;
        }

        .subtitle-text {
            font-size: 1rem;
            opacity: 0.85;
            margin-bottom: 1.2rem;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.3rem 0.8rem;
            background: rgba(76, 175, 80, 0.1);
            border-radius: 999px;
            border: 1px solid rgba(76, 175, 80, 0.45);
            font-size: 0.8rem;
            margin-bottom: 0.7rem;
        }

        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .helper-text {
            font-size: 0.9rem;
            opacity: 0.8;
        }

        /* Contenedor del botón de voz */
        .voice-card {
            margin-top: 1.8rem;
            padding: 1.3rem 1.4rem;
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.15), rgba(156, 39, 176, 0.18));
            border: 1px solid rgba(255,255,255,0.08);
        }

        /* Resultado de texto reconocido */
        .result-box {
            margin-top: 1.2rem;
            padding: 1rem 1.2rem;
            border-radius: 14px;
            background: rgba(12, 12, 25, 0.95);
            border: 1px solid rgba(255,255,255,0.06);
            font-size: 0.95rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ====================== INTERFAZ ======================
# Contenedor principal
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        # Logo / imagen
        image = Image.open("voice_ctrl.jpg")
        st.image(image, use_column_width=True)

    with col2:
        st.markdown('<div class="pill">🟢 <span>MQTT listo</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="title-text">🎙️ Interfaces Multimodales</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle-text">Control por voz conectado a MQTT en tiempo real.</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Cómo usar</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="helper-text">Haz clic en el botón de abajo y habla claramente cerca del micrófono. '
            'El texto será reconocido, mostrado en pantalla, publicado vía MQTT y reproducido por voz.</div>',
            unsafe_allow_html=True,
        )

    # ---------- Sección del botón de escucha ----------
    st.markdown('<div class="voice-card">', unsafe_allow_html=True)
    st.markdown("#### 🎧 Control por voz")

    st.write("Pulsa el botón y empieza a hablar:")

    stt_button = Button(label="🎤 Iniciar reconocimiento", width=260)

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
        override_height=80,
        debounce_time=0,
    )

    st.markdown("</div>", unsafe_allow_html=True)  # cierre voice-card

    # ====================== PROCESAMIENTO DE RESULTADO ======================
    if result and "GET_TEXT" in result:

        with st.spinner("🎧 Escuchando y procesando..."):
            time.sleep(1.5)

        # Texto reconocido
        text = result.get("GET_TEXT").strip()

        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown("##### 🗣️ Texto reconocido")
        st.write(text)

        # Traducir texto
        translator = Translator()
        translated = translator.translate(text, dest="es").text
        st.markdown("##### 🔤 Traducción")
        st.write(translated)

        st.markdown("</div>", unsafe_allow_html=True)

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
