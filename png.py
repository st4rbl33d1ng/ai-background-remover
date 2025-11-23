import streamlit as st
from rembg import remove, new_session
from PIL import Image
from io import BytesIO

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AI Background Remover", page_icon="✂️", layout="wide")

# --- 2. ESTILOS (CSS SEGURO Y DE ALTO CONTRASTE) ---
def inject_custom_css():
    st.markdown("""
        <style>
        /* --- IMPORTAR FUENTE --- */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;700&display=swap');

        /* --- REGLAS GENERALES --- */
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            color: #5483B3; /* Color de texto principal */
        }

        /* FONDO DE LA APP (Degradado Azul Claro) */
        .stApp {
            background: linear-gradient(180deg, #C1E8FF 0%, #E3F2FD 100%);
        }

        /* --- BARRA LATERAL (SIDEBAR) --- */
        [data-testid="stSidebar"] {
            background-color: #C1E8FF;
            border-right: 3px solid #5483B3; /* Borde fuerte para separar */
        }
        
        /* Textos de la barra lateral más visibles */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p {
            color: #5483B3 !important;
            font-weight: 700 !important; /* Negrita fuerte */
            font-size: 1rem !important;
        }

        /* --- TÍTULO PRINCIPAL --- */
        h1 {
            color: #5483B3;
            font-weight: 800;
            text-transform: uppercase;
            text-shadow: 2px 2px 0px #C1E8FF; /* Sombra dura para legibilidad */
        }

        /* --- CAJAS / TARJETAS (Para dar estructura) --- */
        .css-card {
            background-color: rgba(255, 255, 255, 0.5);
            border: 2px solid #5483B3; /* Borde del color fuerte */
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(84, 131, 179, 0.1);
        }

        /* --- ZONA DE SUBIDA DE ARCHIVO --- */
        [data-testid="stFileUploader"] {
            background-color: #C1E8FF;
            border: 3px dashed #5483B3; /* Borde grueso y visible */
            border-radius: 15px;
            padding: 15px;
        }
        /* Texto dentro del uploader */
        [data-testid="stFileUploader"] div {
            color: #5483B3 !important; 
            font-weight: 700;
        }
        /* Botón "Browse files" */
        [data-testid="stFileUploader"] button {
            color: #C1E8FF;
            background-color: #5483B3;
            border: none;
            font-weight: bold;
        }

        /* --- BOTÓN DE DESCARGA --- */
        .stButton > button {
            background-color: #5483B3;
            color: #FFFFFF !important;
            border: 2px solid #C1E8FF;
            border-radius: 25px;
            font-weight: bold;
            font-size: 18px;
            padding: 0.5rem 1rem;
            width: 100%;
            transition: all 0.3s;
        }
        .stButton > button:hover {
            background-color: #7DA0C4;
            border-color: #5483B3;
            color: #FFFFFF !important;
            transform: scale(1.02);
        }

        /* --- RADIO BUTTONS (Simplificados para que funcionen) --- */
        /* Aumentamos el tamaño del texto de las opciones */
        .stRadio label {
            font-size: 18px !important;
            font-weight: 600 !important;
            color: #5483B3 !important;
        }

        </style>
    """, unsafe_allow_html=True)

# --- 3. MODELO (Caché para velocidad) ---
@st.cache_resource
def get_model(model_name):
    return new_session(model_name)

# --- 4. PROGRAMA PRINCIPAL ---
def main():
    inject_custom_css() # Aplicar diseño

    st.title("✂️ AI Background Remover")

    # --- BARRA LATERAL ---
    st.sidebar.header("⚙️ Configuración")

    # Selector de modo (Uso estándar para evitar errores)
    mode = st.sidebar.radio(
        "Nivel de Limpieza:",
        ["Estándar", "Detallado", "Ultra"]
    )

    # --- LÓGICA DE PROCESAMIENTO ---
    rembg_kwargs = {}
    if mode == "Detallado":
        rembg_kwargs = {
            "alpha_matting": True, 
            "alpha_matting_foreground_threshold": 240,
            "alpha_matting_background_threshold": 10, 
            "alpha_matting_erode_size": 10
        }
    elif mode == "Ultra":
        rembg_kwargs = {
            "alpha_matting": True, 
            "alpha_matting_foreground_threshold": 200, 
            "alpha_matting_background_threshold": 50, 
            "alpha_matting_erode_size": 15
        }

    session = get_model("isnet-general-use")

    # --- INTERFAZ DE USUARIO ---
    
    # Contenedor 1: Subida
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Sube tu imagen (JPG, PNG, WEBP)", type=["png", "jpg", "jpeg", "webp"])
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        # Contenedor 2: Resultados
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        image = Image.open(uploaded_file)
        
        with col1:
            st.subheader("Original")
            # Borde azul a la imagen
            st.markdown(
                f'<div style="border: 4px solid #5483B3; border-radius: 10px; overflow: hidden;">', 
                unsafe_allow_html=True
            )
            st.image(image, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.subheader(f"Resultado: {mode}")
            
            # Procesar
            with st.spinner("Procesando..."):
                try:
                    output = remove(image, session=session, **rembg_kwargs)
                    
                    # Mostrar resultado con borde
                    st.markdown(
                        f'<div style="border: 4px solid #5483B3; border-radius: 10px; overflow: hidden;">', 
                        unsafe_allow_html=True
                    )
                    st.image(output, use_column_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Botón de descarga
                    buf = BytesIO()
                    output.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.download_button(
                        label="⬇️ DESCARGAR IMAGEN",
                        data=byte_im,
                        file_name=f"sin_fondo_{mode}.png",
                        mime="image/png",
                    )
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

