import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io

# 1. إعداد الصفحة وتحسين المظهر ليناسب الهواتف والشاشات الكبيرة
st.set_page_config(page_title="Custom AI Studio Flow", layout="wide")

# 2. قراءة مفتاح جوجل والـ Tokens الآمنة تلقائياً من إعدادات Secrets
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception:
    st.error("⚠️ يرجى إضافة مفتاح GOOGLE_API_KEY في إعدادات Secrets الخاصة بالموقع أولاً لكي يعمل التطبيق.")
    st.stop()

# 3. عنوان التطبيق والواجهة
st.title("🎨 استوديو الذكاء الاصطناعي المتكامل")
st.caption("منصتك الخاصة لتوليد النصوص، الصور، والفيديوهات مجاناً بالكامل")

# 4. لوحة التحكم الجانبية (Sidebar) للأوامر والإعدادات
with st.sidebar:
    st.header("🎛️ لوحة التحكم")
    
    # اختيار نوع الخدمة
    mode = st.selectbox("ماذا تريد أن تصنع اليوم؟", [
        "📸 توليد صور (Imagen 3)", 
        "🎬 توليد فيديو سريع", 
        "✍️ مساعد نصوص (Gemini Flash)"
    ])
    
    # صندوق إدخال النص
    prompt = st.text_area("اكتب الوصف (Prompt):", placeholder="اكتب وصفاً دقيقاً باللغة الإنجليزية للحصول على أفضل النتائج...")
    
    # زر البدء والتوليد
    submit_button = st.button("توليد الآن ✨")

# 5. منطقة العرض الرئيسية للنتائج
st.subheader("🖼️ معرض النتائج")

if submit_button and prompt:
    with st.spinner("جاري المعالجة والتوليد، يرجى الانتظار..."):
        try:
            # --- المسار الأول: توليد الصور ---
            if mode == "📸 توليد صور (Imagen 3)":
                imagen = genai.ImageGenerationModel("imagen-3.0-generate-002")
                result = imagen.generate_images(prompt=prompt, number_of_images=1)
                for image in result.images:
                    st.image(image._pil_image, caption="الصورة التي تم توليدها", use_container_width=True)
            
            # --- المسار الثاني: توليد الفيديوهات (عبر خادم مجاني مفتوح) ---
            elif mode == "🎬 توليد فيديو سريع":
                API_URL = "https://huggingface.co"
                
                # إرسال الطلب بدون توكن أو استخدام توكن من الإعدادات إذا رغب المستخدم مستقبلاً
                response = requests.post(API_URL, json={"inputs": prompt})
                if response.status_code == 200:
                    st.video(response.content)
                else:
                    st.error("⚠️ خادم الفيديو المجاني مشغول حالياً، يرجى المحاولة بعد قليل أو تغيير الوصف.")
            
            # --- المسار الثالث: توليد النصوص ---
            elif mode == "✍️ مساعد نصوص (Gemini Flash)":
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                st.write(response.text)
                
        except Exception as e:
            st.error(f"حدث خطأ أثناء التوليد: {e}")
            st.info("تأكد من أنك قمت بنسخ مفتاح الـ API بشكل صحيح في إعدادات Secrets.")
