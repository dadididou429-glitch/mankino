import streamlit as st
from google import genai
import requests

# 1. إعداد الصفحة وتصميمها
st.set_page_config(page_title="Custom AI Studio Flow", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #121212; color: #FFFFFF; }
    h1 { color: #FF4B4B; text-align: center; font-family: 'Arial'; }
    .stButton>button { background-color: #FF4B4B; color: white; border-radius: 8px; width: 100%; }
    .stTextArea>div>div>textarea { background-color: #1E1E1E; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 استوديو الذكاء الاصطناعي الخاص بي")
st.caption("منصتك الخاصة لتوليد النصوص، الصور، والفيديوهات مجاناً بالكامل")

# 2. ربط حساب جوجل بأمان
if "GOOGLE_API_KEY" in st.secrets:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"❌ خطأ في إعدادات جوجل: {e}")
        st.stop()
else:
    st.warning("⚠️ مفتاح GOOGLE_API_KEY غير موجود في إعدادات Secrets.")
    st.stop()

# 3. لوحة التحكم الجانبية
with st.sidebar:
    st.header("🎛️ لوحة التحكم")
    mode = st.selectbox("ماذا تريد أن تصنع اليوم؟", [
        "📸 توليد صور (Imagen 3)", 
        "🎬 توليد فيديو سريع", 
        "✍️ مساعد نصوص (Gemini Flash)"
    ])
    prompt = st.text_area("اكتب الوصف (Prompt):", placeholder="اكتب وصفك هنا بالعربية أو الإنجليزية...")
    submit_button = st.button("توليد الآن ✨")

# 4. منطقة العرض الرئيسية
st.subheader("🖼️ معرض النتائج")

if submit_button and prompt:
    with st.spinner("جاري المعالجة والتوليد، يرجى الانتظار..."):
        try:
            # الترجمة التلقائية إلى الإنجليزية لتفادي مشكلة الروابط الطويلة وحروف العربي
            try:
                translation_response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=f"Translate this prompt into a clean, concise English description for image generation, without any extra text or conversational remarks: {prompt}",
                )
                english_prompt = translation_response.text.strip() if translation_response.text else prompt
            except Exception:
                english_prompt = prompt  # إذا فشل سيرفر جوجل استخدم النص الأصلي

            # --- مسار توليد الصور المحمي والمترجم تلقائياً ---
            if mode == "📸 توليد صور (Imagen 3)":
                IMAGE_API_URL = f"https://pollinations.ai{requests.utils.quote(english_prompt)}?width=1024&height=1024&nologo=true"
                response = requests.get(IMAGE_API_URL, timeout=30)
                
                if response.status_code == 200:
                    st.image(response.content, caption="تم توليد صورتك بنجاح! 🚀", use_container_width=True)
                    
                    st.download_button(
                        label="⬇️ تحميل الصورة إلى هاتفك",
                        data=response.content,
                        file_name="ai_studio_image.jpg",
                        mime="image/jpeg"
                    )
                else:
                    st.error("⚠️ خادم الصور مشغول حالياً، يرجى إعادة الضغط على زر التوليد.")

            # --- مسار توليد الفيديو ---
            elif mode == "🎬 توليد فيديو سريع":
                VIDEO_API_URL = "https://huggingface.co"
                response = requests.post(VIDEO_API_URL, json={"inputs": english_prompt}, timeout=60)
                if response.status_code == 200:
                    st.video(response.content)
                else:
                    st.error("⚠️ خادم الفيديو مشغول حالياً، يرجى المحاولة لاحقاً.")

            # --- مسار مساعد النصوص ---
            elif mode == "✍️ مساعد نصوص (Gemini Flash)":
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt,
                )
                st.write(response.text)

        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء التوليد: {e}")
