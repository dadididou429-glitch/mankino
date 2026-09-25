import streamlit as st
from google import genai
import requests
import io

# 1. Configuration de la page avec un style CSS personnalisé (Mode Sombre et Design Pro)
st.set_page_config(page_title="Custom AI Studio Flow", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #121212; color: #FFFFFF; }
    h1 { color: #FF4B4B; text-align: center; font-family: 'Arial'; }
    .stButton>button { background-color: #FF4B4B; color: white; border-radius: 8px; width: 100%; }
    .stTextArea>div>div>textarea { background-color: #1E1E1E; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 AI Studio Flow Personnel")
st.caption("Votre plateforme privée et 100% gratuite pour générer du texte, des images et des vidéos.")

# 2. Connexion sécurisée à l'API Google
if "GOOGLE_API_KEY" in st.secrets:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Erreur de configuration Google: {e}")
        st.stop()
else:
    st.warning("⚠️ Clé GOOGLE_API_KEY manquante dans les Secrets Streamlit.")
    st.stop()

# 3. Panneau de contrôle latéral (Sidebar)
with st.sidebar:
    st.header("🎛️ Panneau de Contrôle")
    mode = st.selectbox("Que voulez-vous créer ?", [
        "📸 Générer une Image (Imagen 3)", 
        "🎬 Générer une Vidéo Rapide", 
        "✍️ Assistant Texte (Gemini Flash)"
    ])
    prompt = st.text_area("Entrez votre description (Prompt) :", placeholder="Érivez ici en arabe ou en anglais...")
    submit_button = st.button("Générer maintenant ✨")

# 4. Zone d'affichage des résultats
st.subheader("🖼️ Galerie des Résultats")

if submit_button and prompt:
    with st.spinner("Traitement et génération en cours, veuillez patienter..."):
        try:
            # Étape intermédiaire : Traduction/Optimisation automatique en anglais via Gemini pour éviter l'erreur de lien long
            translation_response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=f"Translate this prompt into a clean, concise English description for image generation, without any extra text or conversational remarks: {prompt}",
            )
            english_prompt = translation_response.text.strip() if translation_response.text else prompt

            # --- CAS 1 : GÉNÉRATION D'IMAGE ---
            if mode == "📸 Générer une Image (Imagen 3)":
                # Utilisation d'un endpoint optimisé et sécurisé contre les chaînes trop longues
                IMAGE_API_URL = "https://pollinations.ai"
                payload = {"prompt": english_prompt, "width": 1024, "height": 1024, "nologo": True}
                
                response = requests.post(IMAGE_API_URL, json=payload, timeout=30)
                if response.status_code == 200:
                    st.image(response.content, caption="Votre image générée avec succès ! 🚀", use_container_width=True)
                    
                    # Bouton de téléchargement direct sur le téléphone
                    st.download_button(
                        label="⬇️ Télécharger l'image sur votre appareil",
                        data=response.content,
                        file_name="ai_studio_image.jpg",
                        mime="image/jpeg"
                    )
                else:
                    st.error(f"⚠️ Le serveur d'images est surchargé (Code: {response.status_code}). Veuillez réessayer.")

            # --- CAS 2 : GÉNÉRATION DE VIDÉO ---
            elif mode == "🎬 Générer une Vidéo Rapide":
                VIDEO_API_URL = "https://huggingface.co"
                response = requests.post(VIDEO_API_URL, json={"inputs": english_prompt}, timeout=60)
                if response.status_code == 200:
                    st.video(response.content)
                else:
                    st.error("⚠️ Le serveur vidéo est temporairement occupé, veuillez réessayer dans un instant.")

            # --- CAS 3 : ASSISTANT TEXTE ---
            elif mode == "✍️ Assistant Texte (Gemini Flash)":
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt,
                )
                st.write(response.text)

        except Exception as e:
            st.error(f"❌ Une erreur est survenue : {e}")
