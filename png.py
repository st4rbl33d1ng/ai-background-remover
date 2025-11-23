import streamlit as st
from rembg import remove, new_session
from PIL import Image
from io import BytesIO

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AI Background Remover Pro", page_icon="✂️", layout="wide")

# --- 2. CARGA DEL MODELO (Con Caché) ---
@st.cache_resource
def get_model(model_name):
    return new_session(model_name)

# --- 3. INTERFAZ PRINCIPAL ---
def main():
    st.title("✂️ AI Background Remover Pro")
    st.markdown("Elimina fondos con precisión profesional. Compatible con Móvil y PC.")

    # --- BARRA LATERAL (Configuración) ---
    st.sidebar.header("⚙️ Configuración")
    
    # Aquí recuperamos tu selector de modos
    mode = st.sidebar.radio(
        "Nivel de Limpieza:",
        ["Estándar", "Detallado", "Ultra"],
        help="Estándar: Rápido. Ultra: Mejor para cabello y bordes finos."
    )

    # --- LÓGICA DE LOS MODOS (Tu configuración original) ---
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

    # Cargar el modelo
    session = get_model("isnet-general-use")

    # --- ZONA DE SUBIDA ---
    uploaded_file = st.file_uploader("Sube tu imagen", type=["png", "jpg", "jpeg", "webp"])

    if uploaded_file:
        col1, col2 = st.columns(2)
        
        # Imagen Original
        image = Image.open(uploaded_file)
        with col1:
            st.image(image, caption="Original", use_column_width=True)
        
        # Botón de Procesar
        # En web es mejor procesar automáticamente o con botón. Aquí lo hacemos auto al detectar la imagen.
        with col2:
            with st.spinner(f"Procesando en modo {mode}..."):
                try:
                    # AQUÍ SE APLICA LA CONFIGURACIÓN ULTRA/DETALLADO
                    output = remove(image, session=session, **rembg_kwargs)
                    
                    st.image(output, caption=f"Resultado ({mode})", use_column_width=True)
                    
                    # Preparar descarga
                    buf = BytesIO()
                    output.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="⬇️ Descargar PNG",
                        data=byte_im,
                        file_name=f"sin_fondo_{mode}.png",
                        mime="image/png"
                    )
                except Exception as e:
                    st.error(f"Error procesando imagen: {e}")

if __name__ == "__main__":
    main()
