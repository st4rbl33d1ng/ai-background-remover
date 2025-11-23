import streamlit as st
from rembg import remove, new_session
from PIL import Image
from io import BytesIO
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AI Background Remover Pro", page_icon="✂️", layout="wide")

# --- 2. INYECCIÓN DE CSS PERSONALIZADO (VISIBILIDAD MEJORADA) ---
def inject_custom_css():
    # PALETA ESTRICTA:
    # Fuerte: #5483B3
    # Medio:  #7DA0C4
    # Claro:  #C1E8FF
    
    st.markdown("""
        <style>
        /* --- FUENTE Y GENERAL --- */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            color: #5483B3; /* Color base fuerte */
            font-weight: 500; /* AUMENTADO: Texto base más grueso para mejor lectura */
        }

        /* Fondo Principal */
        .stApp {
            background: linear-gradient(180deg, #C1E8FF 0%, #C1E8FF 60%, #7DA0C4 100%);
        }

        /* --- BARRA LATERAL --- */
        [data-testid="stSidebar"] {
            background-color: #C1E8FF;
            border-right: 3px solid #7DA0C4; /* Borde más grueso */
        }
        
        /* Elementos del Sidebar */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] p {
            color: #5483B3 !important;
            font-weight: 700 !important; /* Negrita fuerte en sidebar */
        }

        /* --- TÍTULOS --- */
        h1 {
            color: #5483B3;
            font-weight: 800; /* Extra negrita */
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 1px 1px 0px #C1E8FF; /* Sombra dura sutil para definición */
        }
        .main-subtitle {
            color: #5483B3; /* Cambiado al tono fuerte para más visibilidad */
            font-weight: 600;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }

        /* --- TARJETAS --- */
        .css-card {
            background: rgba(193, 232, 255, 0.6); /* #C1E8FF más opaco */
            backdrop-filter: blur(8px);
            border-radius: 20px;
            border: 2px solid #5483B3; /* Borde fuerte */
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 8px 16px rgba(84, 131, 179, 0.2);
        }

        /* --- SUBIDA DE ARCHIVO --- */
        [data-testid="stFileUploader"] {
            background: #C1E8FF;
            border-radius: 15px;
            padding: 20px;
            border: 3px dashed #5483B3; /* Borde más grueso y visible */
        }
        [data-testid="stFileUploader"] section > button {
             background-color: #5483B3; /* Botón fuerte */
             color: #C1E8FF;
             font-weight: 800;
             border: none;
             padding: 0.5rem 1rem;
        }
        [data-testid="stFileUploader"] div {
            color: #5483B3;
            font-weight: 600;
        }

        /* --- BOTONES DE ACCIÓN --- */
        .stButton > button {
            background-color: #5483B3;
            color: #C1E8FF !important;
            border: 3px solid #7DA0C4; /* Borde medio para contraste */
            border-radius: 30px;
            padding: 0.7rem 1.5rem;
            font-weight: 800; /* Texto muy grueso */
            transition: all 0.3s ease;
            width: 100%;
            font-size: 1.1rem;
        }
        
        .stButton > button:hover {
            background-color: #7DA0C4;
            color: #ffffff !important; /* Blanco puro al pasar el mouse para máximo brillo */
            border-color: #5483B3;
            transform: scale(1.02);
        }

        /* --- RADIO BUTTONS (BOTEONES DE SELECCIÓN) - REDISEÑADOS --- */
        /* Hacemos que la opción seleccionada sea un bloque sólido del color fuerte */
        label[data-baseweb="radio"][aria-checked="true"] {
            background-color: #5483B3 !important; /* Fondo fuerte al seleccionar */
            padding: 8px 12px !important;
            border-radius: 8px !important;
            margin-bottom: 4px;
            transition: all 0.2s ease;
        }

        /* Cambiamos el color del texto y el círculo dentro de la selección a claro */
        label[data-baseweb="radio"][aria-checked="true"] * {
            color: #C1E8FF !important; /* Texto claro sobre fondo oscuro */
            font-weight: 800 !important;
        }
        /* El círculo del radio seleccionado */
        label[data-baseweb="radio"][aria-checked="true"] > div:first-child {
             border-color: #C1E8FF !important;
             background-color: #5483B3 !important;
        }

        /* Las opciones NO seleccionadas */
        label[data-baseweb="radio"][aria-checked="false"] {
            padding: 8px 12px !important;
             font-weight: 600 !important;
        }


        /* --- IMÁGENES Y SPINNER --- */
        .stImage img {
            border: 4px solid #5483B3; /* Marco fuerte */
            border-radius: 15px;
        }
        .stSpinner > div {
            border-color: #5483B3 transparent #7DA0C4 transparent !important;
        }

        </style>
    """, unsafe_allow_html=True)

# --- 3. MODELO ---
@st.cache_resource
def get_model(model_name):
    return new_session(model_name)

# --- 4. MAIN ---
def main():
    inject_custom_css()

    st.title("✂️ AI Background Remover")
    st.markdown('<p class="main-subtitle">Diseño Puro & Eliminación Precisa</p>', unsafe_allow_html=True)

    # --- SIDEBAR ---
    st.sidebar.header("⚙️ Ajustes")
    
    # Usamos un contenedor para dar un poco de aire a los radios rediseñados
    with st.sidebar.container():
        mode = st.radio(
            "Nivel de Limpieza:",
            ["Estándar", "Detallado", "Ultra"]
        )
    
    st.sidebar.markdown("---")

    # --- LÓGICA ---
    rembg_kwargs = {}
    if mode == "Detallado":
        rembg_kwargs = {"alpha_matting": True, "alpha_matting_foreground_threshold": 240,"alpha_matting_background_threshold": 10, "alpha_matting_erode_size": 10}
    elif mode == "Ultra":
        rembg_kwargs = {"alpha_matting": True, "alpha_matting_foreground_threshold": 200, "alpha_matting_background_threshold": 50, "alpha_matting_erode_size": 15}

    session = get_model("isnet-general-use")

    # --- UI PRINCIPAL ---
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Sube imagen aquí", type=["png", "jpg", "jpeg", "webp"])
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        
        image = Image.open(uploaded_file)
        with col1:
            st.subheader("Original")
            st.image(image, use_column_width=True)
        
        with col2:
            # Usamos un f-string para que el título cambie dinámicamente
            st.subheader(f"Resultado: {mode.upper()}") 
            placeholder = st.empty()
            with placeholder.container():
                 with st.spinner("Procesando con IA..."):
                    try:
                        output = remove(image, session=session, **rembg_kwargs)
                        placeholder.empty()
                        st.image(output, use_column_width=True)
                        
                        buf = BytesIO()
                        output.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.download_button(
                            label="⬇️ DESCARGAR PNG",
                            data=byte_im,
                            file_name=f"clean_{mode}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    except Exception as e:
                        placeholder.empty()
                        st.error(f"Error: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
