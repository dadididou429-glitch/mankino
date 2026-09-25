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

# منطقة العرض الرئيسية
st.subheader("🖼️ معرض النتائج")

if submit_button and prompt:
    with st.spinner("جاري المعالجة والتوليد، يرجى الانتظار..."):
        try:
            # 1. مسار توليد الصور الفوري المباشر للحسابات المجانية
            if mode == "📸 توليد صور (Imagen 3)":
                # استخدام رابط توليد فوري مجاني وسريع ومخصص للصور فقط لمنع ظهور النصوص
                IMAGE_API_URL = f"https://pollinations.ai{requests.utils.quote(prompt)}?width=1024&height=1024&seed=42"
                response = requests.get(IMAGE_API_URL)
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, caption="الصورة التي تم توليدها بنجاح 🚀", use_container_width=True)
                    
                    # زر تحميل الصورة مباشرة للهاتف
                    st.download_button(
                        label="⬇️ تحميل هذه الصورة إلى هاتفك",
                        data=response.content,
                        file_name="generated_image.jpg",
                        mime="image/jpeg"
                    )
                else:
                    st.error("⚠️ خادم الصور مشغول حالياً، يرجى إعادة المحاولة.")

            # 2. مسار توليد الفيديو
            elif mode == "🎬 توليد فيديو سريع":
                VIDEO_API_URL = "https://huggingface.co"
                response = requests.post(VIDEO_API_URL, json={"inputs": prompt}, timeout=60)
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
