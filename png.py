import streamlit as st
from rembg import remove, new_session
from PIL import Image
from io import BytesIO
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AI Background Remover Pro", page_icon="✂️", layout="wide")

# --- 2. INYECCIÓN DE CSS PERSONALIZADO (ESTÉTICA) ---
def inject_custom_css():
    # Paleta: #C1E8FF (Claro), #7DA0C4, #5483B3, #052659, #021024 (Oscuro)
    
    st.markdown("""
        <style>
        /* --- FUENTE Y FONDO GLOBAL --- */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            color: #021024; /* Texto general oscuro por defecto */
        }

        /* Fondo principal */
        .stApp {
            background: linear-gradient(135deg, #C1E8FF 0%, #7DA0C4 100%);
        }

        /* --- BARRA LATERAL (SIDEBAR) - AHORA CLARA --- */
        [data-testid="stSidebar"] {
            background-color: #C1E8FF; /* Color base claro */
            background-image: linear-gradient(180deg, #C1E8FF 0%, #bfdff5 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.5);
            box-shadow: 2px 0 10px rgba(5, 38, 89, 0.05); /* Sombra muy sutil a la derecha */
        }
        
        /* Textos en la barra lateral (Ahora OSCUROS para leerse sobre fondo claro) */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] .stRadio div[role='radiogroup'] > label {
            color: #052659 !important;
            font-weight: 500;
        }

        /* --- TÍTULOS PRINCIPALES --- */
        h1 {
            color: #052659;
            font-weight: 700;
            letter-spacing: -1px;
        }
        .main-subtitle {
            color: #5483B3;
            font-weight: 500;
            margin-bottom: 2rem;
        }

        /* --- CONTENEDORES TIPO "TARJETA" (GLASSMORPHISM) --- */
        .css-card {
            background: rgba(255, 255, 255, 0.4); /* Más transparente y luminoso */
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07); 
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.6);
            padding: 30px;
            margin-bottom: 20px;
        }

        /* --- WIDGET DE SUBIDA DE ARCHIVOS --- */
        [data-testid="stFileUploader"] {
            background: rgba(255, 255, 255, 0.5);
            border-radius: 15px;
            padding: 20px;
            border: 2px dashed #7DA0C4; 
            transition: border-color 0.3s;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: #052659;
        }
        [data-testid="stFileUploader"] section > button {
             background-color: #5483B3;
             color: white;
        }

        /* --- BOTONES (Descarga) --- */
        .stButton > button {
            background: linear-gradient(to right, #052659, #5483B3); /* Degradado oscuro para resaltar */
            color: white !important;
            border: none;
            border-radius: 30px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(5, 38, 89, 0.3);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(5, 38, 89, 0.4);
            background: linear-gradient(to right, #021024, #052659);
        }

        /* Ajuste imágenes */
        .stImage img {
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }

        </style>
    """, unsafe_allow_html=True)

# --- 3. CARGA DEL MODELO (Con Caché) ---
@st.cache_resource
def get_model(model_name):
    return new_session(model_name)

# --- 4. INTERFAZ PRINCIPAL ---
def main():
    # Inyectar estilos
    inject_custom_css()

    st.title("✂️ AI Background Remover Pro")
    st.markdown('<p class="main-subtitle">Herramienta de precisión con estética minimalista.</p>', unsafe_allow_html=True)

    # --- BARRA LATERAL (Ahora clara) ---
    st.sidebar.header("⚙️ Panel de Control")
    
    mode = st.sidebar.radio(
        "Nivel de Limpieza:",
        ["Estándar", "Detallado", "Ultra"],
        help="Estándar: Rápido. Ultra: Mejor para cabello y bordes finos."
    )
    
    # Nota informativa en el sidebar para llenar espacio visualmente
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='background-color: rgba(255,255,255,0.4); padding: 10px; border-radius: 10px; border: 1px solid #7DA0C4; font-size: 0.85rem; color: #052659;'>
        ℹ️ <b>Tip:</b> Usa el modo <i>Ultra</i> si tu imagen tiene cabello suelto o detalles complejos.
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

    # --- ÁREA PRINCIPAL ---
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Sube tu imagen (PNG, JPG, WEBP)", type=["png", "jpg", "jpeg", "webp"])
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        
        image = Image.open(uploaded_file)
        with col1:
            st.subheader("Original")
            st.image(image, use_column_width=True)
        
        with col2:
            st.subheader(f"Resultado ({mode})")
            placeholder = st.empty()
            with placeholder.container():
                 with st.spinner(f"Procesando..."):
                    try:
                        output = remove(image, session=session, **rembg_kwargs)
                        placeholder.empty()
                        st.image(output, use_column_width=True)
                        
                        buf = BytesIO()
                        output.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.download_button(
                            label="⬇️ Descargar PNG",
                            data=byte_im,
                            file_name=f"sin_fondo_{mode}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    except Exception as e:
                        placeholder.empty()
                        st.error(f"Error: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
