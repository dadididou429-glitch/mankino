import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# إعداد الصفحة وتصميمها
st.set_page_config(page_title="Custom AI Studio Flow", layout="wide")

st.title("🎨 استوديو الذكاء الاصطناعي المتكامل")
st.caption("منصتك الخاصة لتوليد النصوص، الصور، والفيديوهات مجاناً بالكامل")

# قراءة مفتاح جوجل مباشرة من إعدادات Secrets
if "GOOGLE_API_KEY" in st.secrets:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"❌ فشل في إعداد مكتبة جوجل: {e}")
        st.stop()
else:
    st.warning("⚠️ لم يتم العثور على GOOGLE_API_KEY. يرجى إضافته في قسم Secrets في لوحة تحكم Streamlit.")
    st.stop()

# لوحة التحكم الجانبية
with st.sidebar:
    st.header("🎛️ لوحة التحكم")
    mode = st.selectbox("ماذا تريد أن تصنع اليوم؟", [
        "📸 توليد صور (Imagen 3)", 
        "🎬 توليد فيديو سريع", 
        "✍️ مساعد نصوص (Gemini Flash)"
    ])
    prompt = st.text_area("اكتب الوصف (Prompt):", placeholder="اكتب وصفاً واضحاً باللغة الإنجليزية للحصول على أفضل النتائج...")
    submit_button = st.button("توليد الآن ✨")

# منطقة العرض الرئيسية
st.subheader("🖼️ معرض النتائج")

if submit_button and prompt:
    with st.spinner("جاري المعالجة والتوليد، يرجى الانتظار..."):
        try:
            # 1. مسار توليد الصور (باستخدام الأسلوب المحدث الصحيح لمنع الخطأ الظاهر)
            if mode == "📸 توليد صور (Imagen 3)":
                result = genai.generate_images(
                    model="imagen-3.0-generate-002",
                    prompt=prompt,
                    number_of_images=1
                )
                
                if result and result.generated_images:
                    for img in result.generated_images:
                        st.image(img.image._pil_image, caption="الصورة الناتجة", use_container_width=True)
                else:
                    st.error("⚠️ استجابة جوجل فارغة، حاول كتابة وصف مختلف.")

            # 2. مسار توليد الفيديو
            elif mode == "🎬 توليد فيديو سريع":
                API_URL = "https://huggingface.co"
                response = requests.post(API_URL, json={"inputs": prompt}, timeout=60)
                if response.status_code == 200:
                    st.video(response.content)
                else:
                    st.error(f"⚠️ خادم الفيديو مشغول حالياً. كود الخطأ: {response.status_code}")

            # 3. مسار توليد النصوص
            elif mode == "✍️ مساعد نصوص (Gemini Flash)":
                text_model = genai.GenerativeModel("gemini-2.5-flash")
                response = text_model.generate_content(prompt)
                st.write(response.text)

        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء التوليد: {e}")
