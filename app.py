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
st.title("🎙️ INTERFACES MULTIMODALES")
st.subheader("CONTROL POR VOZ")

image = Image.open("voice_ctrl.jpg")
st.image(image, width=200)

st.write("Toca el botón y habla...")


# ==== BOTÓN DE ESCUCHA ====
stt_button = Button(label="🎤 Iniciar reconocimiento", width=250)

stt_button.js_on_event("button_click", CustomJS(code="""
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
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# ==== PROCESAMIENTO DE RESULTADO ====
if result and "GET_TEXT" in result:

    with st.spinner("🎧 Escuchando y procesando..."):
        time.sleep(1.5)

    # Texto reconocido
    text = result.get("GET_TEXT").strip()
    st.success(f"🗣️ Texto reconocido: {text}")

    # Traducir texto
    translator = Translator()
    translated = translator.translate(text, dest='es').text
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
