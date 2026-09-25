import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import requests
import io

# إعداد الصفحة وتصميمها
st.set_page_config(page_title="Custom AI Studio Flow", layout="wide")

st.title("🎨 استوديو الذكاء الاصطناعي المتكامل")
st.caption("منصتك الخاصة لتوليد النصوص، الصور، والفيديوهات مجاناً بالكامل")

# ربط الحساب بالمكتبة الجديدة لجوجل عبر الـ Secrets
if "GOOGLE_API_KEY" in st.secrets:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"❌ فشل في إعداد مكتبة جوجل: {e}")
        st.stop()
else:
    st.warning("⚠️ لم يتم العثور على GOOGLE_API_KEY في الإعدادات.")
    st.stop()

# لوحة التحكم الجانبية
with st.sidebar:
    st.header("🎛️ لوحة التحكم")
    mode = st.selectbox("ماذا تريد أن تصنع اليوم؟", [
        "📸 توليد صور (Imagen 3)", 
        "🎬 توليد فيديو سريع", 
        "✍️ مساعد نصوص (Gemini Flash)"
    ])
    prompt = st.text_area("اكتب الوصف (Prompt):", placeholder="اكتب وصفاً واضحاً باللغة الإنجليزية...")
    submit_button = st.button("توليد الآن ✨")

# منطقه العرض الرئيسية
st.subheader("🖼️ معرض النتائج")

if submit_button and prompt:
    with st.spinner("جاري المعالجة والتوليد، يرجى الانتظار..."):
        try:
            # 1. مسار توليد الصور المتوافق مجاناً باستخدام النموذج الأحدث مجاناً لعام 2026
            if mode == "📸 توليد صور (Imagen 3)":
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=f"Generate a beautiful image based on this description: {prompt}",
                )
                
                image_found = False
                if response.candidates:
                    for candidate in response.candidates:
                        if candidate.content and candidate.content.parts:
                            for part in candidate.content.parts:
                                if part.inline_data:
                                    img_data = part.inline_data.data
                                    image = Image.open(io.BytesIO(img_data))
                                    st.image(image, caption="الصورة الناتجة", use_container_width=True)
                                    image_found = True
                
                if not image_found:
                    if response.text:
                        st.write(response.text)
                    else:
                        st.error("⚠️ لم نتمكن من جلب الصورة، يرجى إعادة المحاولة بوصف آخر بالإنجليزية.")

            # 2. مسار توليد الفيديو
            elif mode == "🎬 توليد فيديو سريع":
                API_URL = "https://huggingface.co"
                response = requests.post(API_URL, json={"inputs": prompt}, timeout=60)
                if response.status_code == 200:
                    st.video(response.content)
                else:
                    st.error("⚠️ خادم الفيديو مشغول حالياً، يرجى المحاولة لاحقاً.")

            # 3. مسار توليد النصوص بالمنظومة الحديثة المقترحة من جوجل
            elif mode == "✍️ مساعد نصوص (Gemini Flash)":
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt,
                )
                st.write(response.text)

        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء التوليد: {e}")
