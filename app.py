import io
import time
import numpy as np
from PIL import Image

import streamlit as st
from tensorflow.keras.models import load_model


# ====================== CONFIGURACIÓN DE PÁGINA ======================
st.set_page_config(
    page_title="Cerradura Inteligente",
    page_icon="🔒",
    layout="centered",
)


# ====================== ESTILOS ======================
st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at top left, #101018, #1e1f2b);
            color: #F5F5F5;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        .main-card {
            background: rgba(10, 10, 22, 0.96);
            border-radius: 22px;
            padding: 2.3rem 2.7rem;
            box-shadow: 0 22px 55px rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin-top: 2.2rem;
        }

        .title-text {
            font-size: 2.4rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
        }

        .subtitle-text {
            font-size: 1rem;
            opacity: 0.85;
            margin-bottom: 1.4rem;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.3rem 0.8rem;
            border-radius: 999px;
            font-size: 0.8rem;
            border: 1px solid rgba(46, 204, 113, 0.8);
            background: rgba(46, 204, 113, 0.12);
            margin-bottom: 0.9rem;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        .helper-text {
            font-size: 0.9rem;
            opacity: 0.8;
        }

        .side-card {
            padding: 1rem 1.1rem;
            border-radius: 16px;
            background: rgba(16, 16, 30, 0.96);
            border: 1px solid rgba(255,255,255,0.07);
            font-size: 0.9rem;
        }

        .result-card {
            margin-top: 1.2rem;
            padding: 1.1rem 1.2rem;
            border-radius: 16px;
            background: radial-gradient(circle at top left, rgba(76, 175, 80, 0.18), rgba(25, 214, 162, 0.12));
            border: 1px solid rgba(46, 204, 113, 0.5);
        }

        .chip {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            font-size: 0.8rem;
            border: 1px solid rgba(255,255,255,0.25);
            background: rgba(0,0,0,0.2);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ====================== CARGA DEL MODELO ======================
@st.cache_resource
def load_keras_model():
    model = load_model("keras_model.h5", compile=False)
    return model


@st.cache_resource
def load_labels():
    with open("labels.txt", "r", encoding="utf-8") as f:
        labels = [line.strip() for line in f.readlines()]
    return labels


model = load_keras_model()
labels = load_labels()


# ====================== INTERFAZ ======================
st.markdown('<div class="main-card">', unsafe_allow_html=True)

st.markdown(
    '<div class="title-text">🔒 Cerradura Inteligente</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle-text">Sistema de autenticación mediante reconocimiento visual en tiempo real.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="status-pill">🟢 <span>Modelo cargado</span></div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="section-title">📸 Toma una foto</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="helper-text">Coloca tu rostro frente a la cámara y captura una imagen para '
        'validar el acceso.</div>',
        unsafe_allow_html=True,
    )

    picture = st.camera_input("Toma una foto")

    prediction_label = None
    prediction_conf = None

    if picture is not None:
        with st.spinner("Procesando imagen y verificando acceso..."):
            time.sleep(0.6)

            # ====================== BLOQUE DE PREDICCIÓN ======================
            # Aquí se prepara la imagen y se manda al modelo.
            # Si en tu código original tú preprocesabas distinto,
            # puedes reemplazar SOLO este bloque por el tuyo.
            img = Image.open(io.BytesIO(picture.getvalue())).convert("RGB")
            img = img.resize((224, 224))  # ajusta si tu modelo usa otro tamaño

            data = np.asarray(img, dtype=np.float32)
            # Normalización típica de modelos de Teachable Machine (-1, 1)
            data = (data / 127.5) - 1.0
            data = np.expand_dims(data, axis=0)  # (1, 224, 224, 3)

            preds = model.predict(data)
            index = int(np.argmax(preds))
            prediction_label = labels[index] if index < len(labels) else "Desconocido"
            prediction_conf = float(preds[0][index])
            # ==================== FIN BLOQUE DE PREDICCIÓN ====================

        # Resultados bonitos
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown("#### ✅ Resultado de autenticación")

        if prediction_label is not None:
            st.write(f"**Identificado como:** `{prediction_label}`")
            st.write(f"**Confianza:** {prediction_conf * 100:.2f} %")

            # Ejemplo simple de lógica de acceso visual
            # (ajusta el texto según tus etiquetas reales)
            st.markdown("---")
            if prediction_conf > 0.8:
                st.success("🔓 Acceso concedido")
            else:
                st.error("🔐 Acceso denegado")

        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("### ℹ️ Detalles")
    st.markdown(
        """
        <div class="side-card">
            <div class="section-title">Cómo funciona</div>
            <p class="helper-text">
                1. La cámara captura una imagen.<br>
                2. La imagen se envía a un modelo entrenado en <b>keras_model.h5</b>.<br>
                3. El modelo compara el rostro con las clases definidas en <b>labels.txt</b>.<br>
                4. Según la confianza, se concede o se deniega el acceso.
            </p>
            <br>
            <span class="chip">📁 keras_model.h5</span>
            &nbsp;
            <span class="chip">🏷️ labels.txt</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)
