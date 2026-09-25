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
        # إنشاء العميل الجديد المعتمد من جوجل
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
            # 1. مسار توليد الصور الحديث المعتمد من جوجل
            if mode == "📸 توليد صور (Imagen 3)":
                result = client.models.generate_images(
                    model='imagen-3.0-generate-002',
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        output_mime_type="image/jpeg"
                    )
                )
                
                if result and result.generated_images:
                    for generated_image in result.generated_images:
                        image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                        st.image(image, caption="الصورة الناتجة", use_container_width=True)
                else:
                    st.error("⚠️ لم تقم جوجل بإرجاع أي صورة، جرب تغيير الوصف.")

            # 2. مسار توليد الفيديو
            elif mode == "🎬 توليد فيديو سريع":
                API_URL = "https://huggingface.co"
                response = requests.post(API_URL, json={"inputs": prompt}, timeout=60)
                if response.status_code == 200:
                    st.video(response.content)
                else:
                    st.error("⚠️ خادم الفيديو مشغول حالياً، يرجى المحاولة لاحقاً.")

            # 3. مسار توليد النصوص بالمنظومة الجديدة
            elif mode == "✍️ مساعد نصوص (Gemini Flash)":
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                st.write(response.text)

        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء التوليد: {e}")
