import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# Configuración de la página
st.set_page_config(
    page_title="Lector de Sensor MQTT",
    page_icon="📡",
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
    background: linear-gradient(135deg, #030B1F 0%, #061B45 45%, #003B8E 100%);
    color: #F8FAFC;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020817 0%, #061B45 100%);
    border-right: 1px solid rgba(0, 174, 255, 0.35);
}

section[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

.hero-card {
    background: linear-gradient(135deg, rgba(0, 119, 255, 0.28), rgba(0, 212, 255, 0.12));
    border: 1px solid rgba(0, 212, 255, 0.35);
    border-radius: 28px;
    padding: 34px 38px;
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.35);
    margin-bottom: 28px;
}

.hero-label {
    display: inline-block;
    background: rgba(0, 212, 255, 0.14);
    border: 1px solid rgba(0, 212, 255, 0.45);
    color: #8DEBFF;
    padding: 7px 13px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 14px;
    letter-spacing: 0.4px;
}

.hero-title {
    font-size: 46px;
    font-weight: 800;
    line-height: 1.05;
    color: #FFFFFF;
    margin-bottom: 12px;
    letter-spacing: -1px;
}

.hero-subtitle {
    font-size: 18px;
    line-height: 1.6;
    color: #D7E9FF;
    max-width: 850px;
}

.glass-card {
    background: rgba(255, 255, 255, 0.075);
    border: 1px solid rgba(148, 197, 255, 0.22);
    border-radius: 24px;
    padding: 26px;
    box-shadow: 0 16px 45px rgba(0, 0, 0, 0.22);
    margin-bottom: 22px;
}

.card-title {
    font-size: 22px;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 8px;
}

.card-text {
    font-size: 15px;
    color: #CFE8FF;
    line-height: 1.6;
}

.step-badge {
    display: inline-block;
    background: rgba(0, 119, 255, 0.18);
    border: 1px solid rgba(0, 212, 255, 0.42);
    color: #9EEBFF;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 12px;
}

.status-card {
    background: linear-gradient(135deg, rgba(0, 119, 255, 0.22), rgba(0, 212, 255, 0.08));
    border: 1px solid rgba(0, 212, 255, 0.30);
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 18px;
}

.status-title {
    font-size: 18px;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 6px;
}

.status-text {
    color: #D7E9FF;
    font-size: 14px;
    line-height: 1.5;
}

div.stButton > button {
    background: linear-gradient(135deg, #0077FF 0%, #00D4FF 100%);
    color: #FFFFFF;
    border: none;
    border-radius: 16px;
    padding: 0.8rem 1.2rem;
    font-weight: 800;
    font-size: 16px;
    box-shadow: 0 14px 34px rgba(0, 119, 255, 0.38);
    transition: all 0.25s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 18px 42px rgba(0, 212, 255, 0.38);
    color: #FFFFFF;
}

div.stButton > button:active {
    transform: translateY(0px);
}

[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {
    color: #D7E9FF !important;
    font-weight: 700;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background-color: rgba(255, 255, 255, 0.10);
    color: #FFFFFF;
    border: 1px solid rgba(0, 212, 255, 0.36);
    border-radius: 14px;
}

[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(0, 212, 255, 0.24);
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.18);
}

[data-testid="stMetricLabel"] {
    color: #A9C7EA !important;
    font-weight: 700;
}

[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-weight: 800;
}

.streamlit-expanderHeader {
    font-weight: 700;
    color: #F8FAFC !important;
}

hr {
    border-color: rgba(0, 212, 255, 0.25);
}

.stAlert {
    border-radius: 16px;
}

code {
    border-radius: 14px;
}

.small-note {
    color: #A9C7EA;
    font-size: 14px;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# Variables de estado
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None


def get_mqtt_message(broker, port, topic, client_id):
    """Función para obtener un mensaje MQTT"""
    message_received = {"received": False, "payload": None}

    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            # Si no es JSON, guardar como texto
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True

    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()

        # Esperar máximo 5 segundos
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)

        client.loop_stop()
        client.disconnect()

        return message_received["payload"]

    except Exception as e:
        return {"error": str(e)}


# Sidebar - Configuración
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.markdown("""
    <div class="small-note">
        Define los datos de conexión MQTT antes de solicitar la lectura del sensor.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    broker = st.text_input(
        'Broker MQTT',
        value='broker.mqttdashboard.com',
        help='Dirección del broker MQTT'
    )

    port = st.number_input(
        'Puerto',
        value=1883,
        min_value=1,
        max_value=65535,
        help='Puerto del broker, generalmente 1883'
    )

    topic = st.text_input(
        'Tópico',
        value='Sensor/THP2',
        help='Tópico MQTT a suscribirse'
    )

    client_id = st.text_input(
        'ID del Cliente',
        value='streamlit_client',
        help='Identificador único para este cliente'
    )

    st.divider()

    st.markdown("### 📌 Brokers de prueba")
    st.markdown("""
    - broker.mqttdashboard.com  
    - test.mosquitto.org  
    - broker.hivemq.com
    """)


# Header principal
st.markdown("""
<div class="hero-card">
    <div class="hero-label">MQTT SENSOR DASHBOARD</div>
    <div class="hero-title">Lector de Sensor MQTT</div>
    <div class="hero-subtitle">
        Conecta tu aplicación a un broker MQTT, escucha un tópico específico y visualiza los datos recibidos 
        en una interfaz más clara, moderna y fácil de leer.
    </div>
</div>
""", unsafe_allow_html=True)


# Estructura principal
left_col, right_col = st.columns([1.1, 0.9], gap="large")

with left_col:
    st.markdown("""
    <div class="glass-card">
        <span class="step-badge">PASO 1</span>
        <div class="card-title">Revisa la conexión</div>
        <div class="card-text">
            La configuración del broker, puerto, tópico e ID del cliente se realiza desde el panel lateral.
            Cuando todo esté listo, solicita una lectura para recibir el último mensaje disponible.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="status-card">
        <div class="status-title">📡 Estado de lectura</div>
        <div class="status-text">
            La aplicación esperará hasta 5 segundos por un mensaje publicado en el tópico configurado.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button('🔄 Obtener Datos del Sensor', use_container_width=True):
        with st.spinner('Conectando al broker y esperando datos...'):
            sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
            st.session_state.sensor_data = sensor_data

with right_col:
    st.markdown("""
    <div class="glass-card">
        <span class="step-badge">GUÍA RÁPIDA</span>
        <div class="card-title">Cómo usar esta aplicación</div>
        <div class="card-text">
            1. Configura el broker MQTT en el panel lateral.<br>
            2. Revisa el puerto de conexión.<br>
            3. Escribe el tópico que quieres escuchar.<br>
            4. Define un ID de cliente único.<br>
            5. Presiona el botón para obtener los datos.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander('ℹ️ Información técnica', expanded=False):
        st.markdown("""
        ### Cómo funciona

        Esta aplicación se conecta temporalmente a un broker MQTT, se suscribe al tópico configurado 
        y espera un mensaje durante un máximo de 5 segundos.

        Si el mensaje recibido está en formato JSON, la app lo convierte en métricas individuales.  
        Si el mensaje no es JSON, lo muestra como texto plano.
        """)


# Mostrar resultados
if st.session_state.sensor_data:
    st.divider()

    st.markdown("""
    <div class="glass-card">
        <span class="step-badge">PASO 2</span>
        <div class="card-title">Datos recibidos</div>
        <div class="card-text">
            Aquí se muestra la información recibida desde el tópico MQTT configurado.
        </div>
    </div>
    """, unsafe_allow_html=True)

    data = st.session_state.sensor_data

    # Verificar si hay error
    if isinstance(data, dict) and 'error' in data:
        st.error(f"❌ Error de conexión: {data['error']}")
    else:
        st.success('✅ Datos recibidos correctamente')

        # Mostrar datos en formato JSON
        if isinstance(data, dict):
            # Mostrar cada campo en una métrica
            cols = st.columns(len(data))
            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.metric(label=key, value=value)

            # Mostrar JSON completo
            with st.expander('Ver JSON completo'):
                st.json(data)
        else:
            # Si no es diccionario, mostrar como texto
            st.code(data)
