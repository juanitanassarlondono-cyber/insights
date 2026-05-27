import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""


def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# Streamlit
st.set_page_config(
    page_title='Tablero Inteligente',
    page_icon="🎨",
    layout="wide"
)

# Estilos visuales
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #06142E 0%, #071E4A 45%, #0B2D6B 100%);
    color: #F8FAFC;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #031A3D 0%, #06142E 100%);
    border-right: 1px solid rgba(0, 119, 255, 0.35);
}

section[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

.hero-card {
    background: linear-gradient(135deg, rgba(0, 119, 255, 0.22), rgba(0, 212, 255, 0.12));
    border: 1px solid rgba(0, 212, 255, 0.35);
    border-radius: 26px;
    padding: 34px 38px;
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.35);
    margin-bottom: 28px;
}

.hero-title {
    font-size: 48px;
    font-weight: 800;
    line-height: 1.05;
    margin-bottom: 12px;
    color: #FFFFFF;
    letter-spacing: -1px;
}

.hero-subtitle {
    font-size: 18px;
    line-height: 1.6;
    color: #CFE8FF;
    max-width: 820px;
}

.section-card {
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(148, 197, 255, 0.22);
    border-radius: 22px;
    padding: 26px;
    box-shadow: 0 16px 50px rgba(0, 0, 0, 0.22);
    margin-bottom: 20px;
}

.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 8px;
}

.section-text {
    font-size: 15px;
    color: #D7E9FF;
    line-height: 1.6;
}

.step-badge {
    display: inline-block;
    background: rgba(0, 212, 255, 0.14);
    border: 1px solid rgba(0, 212, 255, 0.38);
    color: #8DEBFF;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 12px;
}

div.stButton > button {
    background: linear-gradient(135deg, #0077FF 0%, #00D4FF 100%);
    color: #FFFFFF;
    border: none;
    border-radius: 14px;
    padding: 0.75rem 1.2rem;
    font-weight: 700;
    font-size: 16px;
    box-shadow: 0 12px 30px rgba(0, 119, 255, 0.35);
    transition: all 0.25s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 38px rgba(0, 212, 255, 0.35);
    color: #FFFFFF;
}

div.stButton > button:active {
    transform: translateY(0px);
}

[data-testid="stTextInput"] label {
    color: #D7E9FF !important;
    font-weight: 700;
}

[data-testid="stTextInput"] input {
    background-color: rgba(255, 255, 255, 0.10);
    color: #FFFFFF;
    border: 1px solid rgba(0, 212, 255, 0.35);
    border-radius: 14px;
}

[data-testid="stSlider"] label {
    font-weight: 700;
}

hr {
    border-color: rgba(0, 212, 255, 0.25);
}

.stAlert {
    border-radius: 16px;
}

canvas {
    border-radius: 20px !important;
    border: 2px solid rgba(0, 212, 255, 0.45) !important;
    box-shadow: 0 14px 45px rgba(0, 0, 0, 0.28);
}

.result-box {
    background: rgba(0, 119, 255, 0.12);
    border-left: 5px solid #00D4FF;
    border-radius: 18px;
    padding: 22px;
    color: #F8FAFC;
    margin-top: 18px;
}

.small-note {
    color: #A9C7EA;
    font-size: 14px;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# Encabezado principal
st.markdown("""
<div class="hero-card">
    <div class="hero-title">Tablero Inteligente</div>
    <div class="hero-subtitle">
        Dibuja un boceto en el panel, analiza la imagen con inteligencia artificial 
        y, si quieres, crea una historia infantil a partir de la descripción generada.
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar reorganizado
with st.sidebar:
    st.markdown("## ⚙️ Panel de control")
    st.markdown("""
    <div class="section-text">
        Ajusta las opciones del boceto antes de analizar la imagen.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### ✏️ Configuración del dibujo")
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)

    st.divider()

    st.markdown("### ℹ️ Acerca de")
    st.markdown("""
    Esta aplicación permite que una máquina interprete un boceto dibujado por el usuario 
    y genere una descripción en español.
    """)

    st.markdown("""
    <div class="small-note">
        Consejo: usa trazos claros y evita llenar demasiado el lienzo para obtener mejores resultados.
    </div>
    """, unsafe_allow_html=True)

# Variables del canvas
drawing_mode = "freedraw"
stroke_color = "#000000"
bg_color = '#FFFFFF'

# Estructura principal en columnas
left_col, right_col = st.columns([1.15, 0.85], gap="large")

with left_col:
    st.markdown("""
    <div class="section-card">
        <span class="step-badge">PASO 1</span>
        <div class="section-title">Dibuja tu boceto</div>
        <div class="section-text">
            Usa el lienzo para hacer un dibujo simple. Luego ingresa tu clave y presiona el botón de análisis.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Create a canvas component
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=300,
        width=400,
        drawing_mode=drawing_mode,
        key="canvas",
    )

with right_col:
    st.markdown("""
    <div class="section-card">
        <span class="step-badge">PASO 2</span>
        <div class="section-title">Analiza la imagen</div>
        <div class="section-text">
            Ingresa tu API key para conectar la aplicación con OpenAI y generar una descripción breve del boceto.
        </div>
    </div>
    """, unsafe_allow_html=True)

    ke = st.text_input('Ingresa tu Clave', type="password")
    os.environ['OPENAI_API_KEY'] = ke

    # Retrieve the OpenAI API Key
    api_key = os.environ['OPENAI_API_KEY']

    # Initialize the OpenAI client with the API key
    client = OpenAI(api_key=api_key)

    analyze_button = st.button("🔎 Analiza la imagen", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        # Encode the image
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
        input_image.save('img.png')

        # Codificar la imagen en base64
        base64_image = encode_image_to_base64("img.png")
        st.session_state.base64_image = base64_image

        prompt_text = (f"Describe in spanish briefly the image")

        # Make the request to the OpenAI API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )

            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response + "▌")

            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)

            # Guardar en session_state
            st.session_state.full_response = full_response
            st.session_state.analysis_done = True

            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content

        except Exception as e:
            st.error(f"An error occurred: {e}")

# Mostrar la funcionalidad de crear historia si ya se hizo el análisis
if st.session_state.analysis_done:
    st.divider()

    st.markdown("""
    <div class="section-card">
        <span class="step-badge">PASO 3</span>
        <div class="section-title">Crea una historia infantil</div>
        <div class="section-text">
            Usa la descripción generada por la inteligencia artificial para convertir tu boceto en una historia breve,
            creativa y apropiada para niños.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📚 ¿Quieres crear una historia?")

    if st.button("✨ Crear historia infantil"):
        with st.spinner("Creando historia..."):
            story_prompt = f"Basándote en esta descripción: '{st.session_state.full_response}', crea una historia infantil breve y entretenida. La historia debe ser creativa y apropiada para niños."

            story_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": story_prompt}],
                max_tokens=500,
            )

            st.markdown("**📖 Tu historia:**")
            st.write(story_response.choices[0].message.content)

# Warnings for user action required
if not api_key:
    st.warning("Por favor ingresa tu API key.")
