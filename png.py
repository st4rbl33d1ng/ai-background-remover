import streamlit as st
from rembg import remove, new_session
from PIL import Image
from io import BytesIO
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AI Background Remover Pro", page_icon="✂️", layout="wide")

# --- 2. INYECCIÓN DE CSS PERSONALIZADO (ESTRICTO 3 COLORES) ---
def inject_custom_css():
    # PALETA:
    # Color 1 (Texto/Fuerte): #5483B3
    # Color 2 (Medio/Bordes): #7DA0C4
    # Color 3 (Fondo/Luz):    #C1E8FF
    
    st.markdown("""
        <style>
        /* --- FUENTE Y GENERAL --- */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            color: #5483B3; /* Todo el texto usa el azul más fuerte */
        }

        /* Fondo Principal: Un degradado muy sutil entre el claro y el medio */
        .stApp {
            background: linear-gradient(180deg, #C1E8FF 0%, #C1E8FF 80%, #7DA0C4 100%);
        }

        /* --- BARRA LATERAL --- */
        [data-testid="stSidebar"] {
            background-color: #C1E8FF;
            border-right: 2px solid #7DA0C4; /* Separación con el azul medio */
        }
        
        /* Elementos del Sidebar */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] p {
            color: #5483B3 !important;
            font-weight: 600; /* Negrita para mejorar lectura sin usar negro */
        }

        /* --- TÍTULOS --- */
        h1 {
            color: #5483B3;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 2px 2px 0px #C1E8FF; /* Sombra dura clara */
        }
        .main-subtitle {
            color: #7DA0C4; /* Subtítulo en tono medio */
            font-weight: 600;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }

        /* --- TARJETAS (GLASSMORPHISM AZULADO) --- */
        .css-card {
            background: rgba(125, 160, 196, 0.15); /* #7DA0C4 con mucha transparencia */
            backdrop-filter: blur(5px);
            border-radius: 20px;
            border: 2px solid #7DA0C4; /* Borde sólido en tono medio */
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 20px rgba(84, 131, 179, 0.15); /* Sombra usando #5483B3 bajito */
        }

        /* --- SUBIDA DE ARCHIVO --- */
        [data-testid="stFileUploader"] {
            background: #C1E8FF;
            border-radius: 15px;
            padding: 20px;
            border: 2px dashed #5483B3; /* Borde fuerte discontinuo */
        }
        [data-testid="stFileUploader"] section > button {
             background-color: #7DA0C4;
             color: #C1E8FF; /* Texto claro sobre botón medio */
             font-weight: bold;
             border: none;
        }
        [data-testid="stFileUploader"] div {
            color: #5483B3;
        }

        /* --- BOTONES DE ACCIÓN --- */
        .stButton > button {
            background-color: #5483B3; /* El color más fuerte para el botón principal */
            color: #C1E8FF !important; /* Texto claro */
            border: 2px solid #C1E8FF;
            border-radius: 30px;
            padding: 0.6rem 1.5rem;
            font-weight: 700;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            background-color: #7DA0C4;
            color: #fff !important;
            border-color: #5483B3;
            transform: scale(1.02);
        }

        /* --- RADIO BUTTONS (SELECCIÓN) --- */
        div[role="radiogroup"] > label > div:first-child {
            background-color: #C1E8FF !important;
            border-color: #5483B3 !important;
        }
        div[role="radiogroup"] > label[data-baseweb="radio"] {
            background-color: transparent !important;
        }

        /* --- IMÁGENES --- */
        .stImage img {
            border: 4px solid #C1E8FF; /* Marco tipo foto */
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(84, 131, 179, 0.3);
        }

        /* Spinner */
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
    
    mode = st.sidebar.radio(
        "Nivel de Limpieza:",
        ["Estándar", "Detallado", "Ultra"]
    )
    
    # Caja de info con los colores permitidos
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='background-color: #C1E8FF; padding: 15px; border-radius: 10px; border: 2px solid #5483B3; color: #5483B3;'>
        <b>💡 Nota:</b><br>
        Para cabellos o pelaje, selecciona el modo <b>Ultra</b>.
        </div>
        """, 
        unsafe_allow_html=True
    )

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
            st.subheader(f"Resultado")
            placeholder = st.empty()
            with placeholder.container():
                 with st.spinner("Trabajando..."):
                    try:
                        output = remove(image, session=session, **rembg_kwargs)
                        placeholder.empty()
                        st.image(output, use_column_width=True)
                        
                        buf = BytesIO()
                        output.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.download_button(
                            label="⬇️ GUARDAR PNG",
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
