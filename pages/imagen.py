import paho.mqtt.client as paho
import time
import json
import streamlit as st
import cv2
import numpy as np
from PIL import Image as Image, ImageOps as ImagOps
from keras.models import load_model

# --- Configuración de página ---
st.set_page_config(page_title="Cerradura Inteligente", page_icon="🔒")

# --- Estilos solo visuales (no afectan la lógica) ---
st.markdown(
    """
    <style>
        .stApp {
            background: #05060b;
            color: #F5F5F5;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        .lock-card {
            background: rgba(12, 12, 22, 0.98);
            border-radius: 24px;
            padding: 2.4rem 2.7rem;
            box-shadow: 0 20px 55px rgba(0, 0, 0, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin-top: 2.8rem;
        }

        .lock-title {
            font-size: 2.4rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
        }

        .lock-subtitle {
            font-size: 1rem;
            opacity: 0.85;
            margin-bottom: 1.4rem;
        }

        .helper-text {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 1rem;
        }

        .status-box {
            margin-top: 1.4rem;
            padding: 1rem 1.3rem;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(46, 204, 113, 0.16), rgba(39, 174, 96, 0.12));
            border: 1px solid rgba(46, 204, 113, 0.5);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Funciones de callback MQTT ---
def on_publish(client, userdata, result):  # create function for callback
    print("El dato ha sido publicado\n")
    pass


def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)


# --- Configuración del cliente MQTT ---
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("APP_CERR")
client1.on_message = on_message
client1.on_publish = on_publish
client1.connect(broker, port)

# --- Cargar modelo Keras ---
model = load_model('keras_model.h5')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# --- Interfaz Streamlit ---
st.markdown('<div class="lock-card">', unsafe_allow_html=True)

st.markdown('<div class="lock-title">Cerradura Inteligente</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="lock-subtitle">Control de apertura y cierre mediante gestos detectados por cámara.</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1.2, 1.8])

with col1:
    st.markdown("#### 🧾 Instrucciones")
    st.markdown(
        '<div class="helper-text">'
        '1. Colócate frente a la cámara.<br>'
        '2. Realiza el gesto configurado para abrir o cerrar.<br>'
        '3. El modelo analiza la imagen y envía el comando por MQTT.'
        '</div>',
        unsafe_allow_html=True,
    )

with col2:
    img_file_buffer = st.camera_input("Toma una Foto")

# --- Lógica original de procesamiento de imagen y gestos ---
if img_file_buffer is not None:
    # Convertir la imagen en formato adecuado
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    img = Image.open(img_file_buffer)

    newsize = (224, 224)
    img = img.resize(newsize)
    img_array = np.array(img)

    # Normalizar imagen
    normalized_image_array = (img_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array

    # Ejecutar predicción
    prediction = model.predict(data)
    print(prediction)

    # --- Detección de gestos ---
    if prediction[0][0] > 0.3:
        st.header('Abriendo 🚪')
        # Publica en el mismo topic y con JSON válido
        client1.publish("ZuluMikerCasa", json.dumps({"gesto": "Abre"}), qos=0, retain=False)
        time.sleep(0.2)

    if prediction[0][1] > 0.3:
        st.header('Cerrando 🔒')
        client1.publish("ZuluMikerCasa", json.dumps({"gesto": "Cierra"}), qos=0, retain=False)
        time.sleep(0.2)

st.markdown("</div>", unsafe_allow_html=True)
