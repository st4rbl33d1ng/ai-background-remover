import streamlit as st
from rembg import remove, new_session
from PIL import Image
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="AI Background Remover", page_icon="✂️", layout="wide")

# Cargar modelo (con caché para que sea rápido)
@st.cache_resource
def get_model(model_name):
    return new_session(model_name)

def main():
    st.title("✂️ Removedor de Fondos con IA")
    st.write("Sube una imagen y la IA eliminará el fondo automáticamente.")

    # Cargar modelo en segundo plano
    session = get_model("isnet-general-use")

    # Subir archivo
    uploaded_file = st.file_uploader("Sube tu imagen (JPG, PNG, WEBP)", type=["png", "jpg", "jpeg", "webp"])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        # Mostrar imagen original
        image = Image.open(uploaded_file)
        with col1:
            st.image(image, caption="Original", use_column_width=True)

        # Procesar
        with col2:
            with st.spinner('Procesando... (esto puede tardar unos segundos)'):
                try:
                    # Quitar fondo
                    output = remove(image, session=session)
                    st.image(output, caption="Sin Fondo", use_column_width=True)

                    # Botón de descarga
                    buf = BytesIO()
                    output.save(buf, format="PNG")
                    byte_im = buf.getvalue()

                    st.download_button(
                        label="⬇️ Descargar Imagen PNG",
                        data=byte_im,
                        file_name="sin_fondo.png",
                        mime="image/png"
                    )
                except Exception as e:
                    st.error(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
