import streamlit as st
from rembg import remove, new_session
from PIL import Image
from io import BytesIO

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AI Background Remover", page_icon="✂️", layout="wide")

# --- 2. ESTILOS CSS (DISEÑO) ---
def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            color: #5483B3;
        }

        .stApp {
            background: linear-gradient(180deg, #C1E8FF 0%, #E3F2FD 100%);
        }

        /* --- ESTILO DEL BOTÓN DE INSTAGRAM --- */
        .insta-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background-color: transparent;
            border: 2px solid #5483B3;
            color: #5483B3 !important;
            padding: 8px 16px;
            border-radius: 50px;
            text-decoration: none !important;
            font-weight: 700;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            margin-top: -10px; /* Ajuste para pegarlo al título */
            margin-bottom: 20px;
        }
        
        .insta-btn:hover {
            background-color: #5483B3;
            color: #FFFFFF !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(84, 131, 179, 0.3);
        }
        
        .insta-btn svg {
            stroke: currentColor; /* El icono toma el color del texto */
        }

        /* --- BARRA LATERAL --- */
        [data-testid="stSidebar"] {
            background-color: #C1E8FF;
            border-right: 3px solid #5483B3;
        }
        [data-testid="stSidebar"] * {
            color: #5483B3 !important;
        }

        /* --- TÍTULOS Y TEXTOS --- */
        h1 {
            color: #5483B3;
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 0.5rem; /* Poco espacio abajo para poner el link */
        }
        
        /* --- CAJAS --- */
        .css-card {
            background-color: rgba(255, 255, 255, 0.5);
            border: 2px solid #5483B3;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
        }

        /* --- UPLOADER --- */
        [data-testid="stFileUploader"] {
            background-color: #C1E8FF;
            border: 3px dashed #5483B3;
            border-radius: 15px;
            padding: 15px;
        }
        [data-testid="stFileUploader"] div {
            color: #5483B3 !important; 
            font-weight: 700;
        }
        [data-testid="stFileUploader"] button {
            color: #C1E8FF;
            background-color: #5483B3;
            border: none;
            font-weight: bold;
        }

        /* --- BOTÓN DESCARGA --- */
        .stButton > button {
            background-color: #5483B3;
            color: #FFFFFF !important;
            border: 2px solid #C1E8FF;
            border-radius: 25px;
            font-weight: bold;
            padding: 0.5rem 1rem;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #7DA0C4;
            color: white !important;
            border-color: #5483B3;
        }
        
        /* --- RADIO BUTTONS --- */
        .stRadio label {
            font-size: 16px !important;
            font-weight: 600 !important;
            color: #5483B3 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 3. MODELO ---
@st.cache_resource
def get_model(model_name):
    return new_session(model_name)

# --- 4. INTERFAZ PRINCIPAL ---
def main():
    inject_custom_css()

    # 1. TÍTULO
    st.title("✂️ AI Background Remover")
    
    # 2. BOTÓN DE INSTAGRAM (Aquí es donde lo insertamos bajo el título)
    # CAMBIA EL LINK POR EL TUYO
    instagram_link = "https://www.instagram.com/st4rbl33d1ng"
    
    st.markdown(f"""
        <a href="{instagram_link}" target="_blank" class="insta-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
            </svg>
            Sígueme en Instagram
        </a>
    """, unsafe_allow_html=True)

    # --- BARRA LATERAL ---
    st.sidebar.header("⚙️ Configuración")
    mode = st.sidebar.radio(
        "Nivel de Limpieza:",
        ["Estándar", "Detallado", "Ultra"]
    )

    # Lógica de parámetros
    rembg_kwargs = {}
    if mode == "Detallado":
        rembg_kwargs = {"alpha_matting": True, "alpha_matting_foreground_threshold": 240, "alpha_matting_background_threshold": 10, "alpha_matting_erode_size": 10}
    elif mode == "Ultra":
        rembg_kwargs = {"alpha_matting": True, "alpha_matting_foreground_threshold": 200, "alpha_matting_background_threshold": 50, "alpha_matting_erode_size": 15}

    session = get_model("isnet-general-use")

    # --- ÁREA DE TRABAJO ---
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Sube tu imagen (JPG, PNG, WEBP)", type=["png", "jpg", "jpeg", "webp"])
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        image = Image.open(uploaded_file)
        
        with col1:
            st.subheader("Original")
            st.markdown('<div style="border: 3px solid #5483B3; border-radius: 10px; overflow: hidden;">', unsafe_allow_html=True)
            st.image(image, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.subheader(f"Resultado: {mode}")
            with st.spinner("Procesando..."):
                try:
                    output = remove(image, session=session, **rembg_kwargs)
                    
                    st.markdown('<div style="border: 3px solid #5483B3; border-radius: 10px; overflow: hidden;">', unsafe_allow_html=True)
                    st.image(output, use_column_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
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

