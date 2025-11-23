import streamlit as st
from rembg import remove, new_session
from PIL import Image
from io import BytesIO
import base64

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AI Background Remover Pro", page_icon="✂️", layout="wide")

# --- 2. INYECCIÓN DE CSS PERSONALIZADO (ESTÉTICA) ---
def inject_custom_css():
    # Paleta de colores de la imagen proporcionada
    # C1E8FF (Lightest), 7DA0C4, 5483B3, 052659, 021024 (Darkest)
    
    st.markdown("""
        <style>
        /* --- FUENTE Y FONDO GLOBAL --- */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }

        /* Fondo principal con un degradado suave y luminoso */
        .stApp {
            background: linear-gradient(135deg, #C1E8FF 0%, #7DA0C4 100%);
        }

        /* --- BARRA LATERAL (SIDEBAR) --- */
        [data-testid="stSidebar"] {
            background: linear-gradient(to bottom, #052659, #021024);
            border-right: 1px solid #5483B3;
        }
        
        /* Textos en la barra lateral para que sean legibles (blanco/claro) */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] .stRadio div[role='radiogroup'] > label {
            color: #C1E8FF !important;
        }

        /* --- TÍTULOS PRINCIPALES --- */
        h1 {
            color: #021024;
            font-weight: 600;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .main-subtitle {
            color: #052659;
            font-weight: 400;
            margin-bottom: 2rem;
        }

        /* --- CONTENEDORES TIPO "TARJETA" (GLASSMORPHISM) --- */
        /* Esto es clave para quitar el aspecto plano. Crea cajas semitransparentes. */
        .css-card {
            background: rgba(255, 255, 255, 0.25); /* Blanco semitransparente */
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15); /* Sombra azulada suave */
            backdrop-filter: blur(8px); /* Efecto de desenfoque de fondo */
            -webkit-backdrop-filter: blur(8px);
            border-radius: 20px; /* Bordes muy redondeados */
            border: 1px solid rgba(255, 255, 255, 0.18); /* Borde sutil brillante */
            padding: 25px;
            margin-bottom: 20px;
        }

        /* --- WIDGET DE SUBIDA DE ARCHIVOS --- */
        [data-testid="stFileUploader"] {
            background: rgba(255, 255, 255, 0.4);
            border-radius: 15px;
            padding: 15px;
            border: 2px dashed #5483B3; /* Borde discontinuo azul medio */
        }
        [data-testid="stFileUploader"] section > button {
             background-color: #5483B3; /* Color del botón de 'Browse files' */
        }

        /* --- BOTONES (Descarga) --- */
        .stButton > button {
            background: linear-gradient(to right, #5483B3, #052659);
            color: white !important;
            border: none;
            border-radius: 30px; /* Forma de píldora */
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(84, 131, 179, 0.4); /* Sombra azul brillante */
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px); /* Efecto de elevación al pasar el mouse */
            box-shadow: 0 8px 25px rgba(84, 131, 179, 0.6);
            background: linear-gradient(to right, #7DA0C4, #5483B3);
        }
        
        /* Ajuste de las imágenes dentro de las columnas para que no toquen los bordes de la tarjeta */
        .stImage img {
            border-radius: 12px;
        }

        </style>
    """, unsafe_allow_html=True)

# --- 3. CARGA DEL MODELO (Con Caché) ---
@st.cache_resource
def get_model(model_name):
    return new_session(model_name)

# --- 4. INTERFAZ PRINCIPAL ---
def main():
    # Inyectar los estilos primero
    inject_custom_css()

    st.title("✂️ AI Background Remover Pro")
    st.markdown('<p class="main-subtitle">Elimina fondos con precisión profesional y una estética moderna.</p>', unsafe_allow_html=True)

    # --- BARRA LATERAL (Configuración) ---
    st.sidebar.header("⚙️ Configuración")
    
    mode = st.sidebar.radio(
        "Nivel de Limpieza:",
        ["Estándar", "Detallado", "Ultra"],
        help="Estándar: Rápido. Ultra: Mejor para cabello y bordes finos."
    )

    # --- LÓGICA DE LOS MODOS ---
    rembg_kwargs = {}
    if mode == "Detallado":
        rembg_kwargs = {"alpha_matting": True, "alpha_matting_foreground_threshold": 240,"alpha_matting_background_threshold": 10, "alpha_matting_erode_size": 10}
    elif mode == "Ultra":
        rembg_kwargs = {"alpha_matting": True, "alpha_matting_foreground_threshold": 200, "alpha_matting_background_threshold": 50, "alpha_matting_erode_size": 15}

    session = get_model("isnet-general-use")

    # --- ZONA DE SUBIDA (Envuesta en una "tarjeta" visual) ---
    st.markdown('<div class="css-card">', unsafe_allow_html=True) # Inicio Tarjeta Superior
    uploaded_file = st.file_uploader("Sube tu imagen (PNG, JPG, WEBP)", type=["png", "jpg", "jpeg", "webp"])
    st.markdown('</div>', unsafe_allow_html=True) # Fin Tarjeta Superior


    if uploaded_file:
        # Usamos un contenedor principal para los resultados
        st.markdown('<div class="css-card">', unsafe_allow_html=True) # Inicio Tarjeta Resultados
        
        col1, col2 = st.columns(2, gap="large")
        
        # Imagen Original
        image = Image.open(uploaded_file)
        with col1:
            st.subheader("Original")
            st.image(image, use_column_width=True)
        
        # Botón de Procesar y Resultado
        with col2:
            st.subheader(f"Resultado ({mode})")
            # Usamos un placeholder para que el spinner esté centrado y bonito
            placeholder = st.empty()
            with placeholder.container():
                 with st.spinner(f"Procesando con inteligencia artificial..."):
                    try:
                        output = remove(image, session=session, **rembg_kwargs)
                        # Limpiamos el spinner y mostramos la imagen
                        placeholder.empty()
                        st.image(output, use_column_width=True)
                        
                        # Preparar descarga
                        buf = BytesIO()
                        output.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        
                        st.markdown("<br>", unsafe_allow_html=True) # Espacio
                        st.download_button(
                            label="⬇️ Descargar PNG sin fondo",
                            data=byte_im,
                            file_name=f"sin_fondo_{mode}.png",
                            mime="image/png",
                            use_container_width=True # Botón ancho completo en su columna
                        )
                    except Exception as e:
                        placeholder.empty()
                        st.error(f"Error procesando imagen: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True) # Fin Tarjeta Resultados

if __name__ == "__main__":
    main()
