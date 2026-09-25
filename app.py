import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# إعداد مفتاح الأي بي آي الخاص بجوجل
# استبدل هذا بمفتاحك الشخصي أو قم بتعيينه كمتغير بيئي
GOOGLE_API_KEY = "YOUR_FREE_GOOGLE_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Custom AI Studio Flow", layout="wide")
st.title("🎨 استوديو الذكاء الاصطناعي الخاص بي")
st.caption("توليد نصوص وصور مجاناً بالكامل باستخدام تقنيات Google")

# تقسيم الواجهة إلى لوحة تحكم جانبية ومساحة عرض
with st.sidebar:
    st.header("🎛️ لوحة التحكم")
    model_type = st.selectbox("اختر نوع التوليد:", ["توليد صور (Imagen 3)", "مساعد نصوص (Gemini Flash)"])
    prompt = st.text_area("اكتب الوصف (Prompt) هنا:", placeholder="مثال: رائد فضاء يركب خيلاً على المريخ، أسلوب سينمائي...")
    submit_button = st.button("توليد الآن ✨")

# منطقة العرض الرئيسية
st.subheader("🖼️ معرض النتائج")

if submit_button and prompt:
    with st.spinner("جاري المعالجة والتوليد..."):
        try:
            if model_type == "توليد صور (Imagen 3)":
                # استدعاء نموذج الصور من جوجل
                imagen = genai.ImageGenerationModel("imagen-3.0-generate-002")
                result = imagen.generate_images(prompt=prompt, number_of_images=1)
                
                # عرض الصورة الناتجة
                for image in result.images:
                    st.image(image._pil_image, caption="الصورة الناتجة", use_container_width=True)
                    
            elif model_type == "مساعد نصوص (Gemini Flash)":
                # استدعاء نموذج النصوص
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                st.write(response.text)
                
        except Exception as e:
            st.error(f"حدث خطأ أثناء التوليد: {e}")
