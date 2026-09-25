import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

# 1. إعداد واجهة الصفحة بالمظهر الداكن الفخم
st.set_page_config(page_title="Custom AI Studio Flow", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0f1115; color: #e4e6eb; }
    h1 { color: #4a90e2; text-align: center; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { background-color: #4a90e2; color: white; border-radius: 20px; font-weight: bold; width: 100%; border: none; }
    .stTextArea>div>div>textarea { background-color: #1b1f27; color: white; border-radius: 10px; border: 1px solid #2e3542; }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 استوديو الذكاء الاصطناعي الخاص بي")
st.caption("النسخة الرسمية المستقرة والمباشرة عبر خوادم Google المعتمدة")

# 2. التحقق من وجود مفتاح الربط الآمن
if "GOOGLE_API_KEY" in st.secrets:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"❌ خطأ في الاتصال بجوجل: {e}")
        st.stop()
else:
    st.warning("⚠️ يرجى التأكد من إضافة GOOGLE_API_KEY في إعدادات Secrets.")
    st.stop()

# 3. لوحة التحكم الجانبية
with st.sidebar:
    st.header("🎛️ لوحة التحكم")
    mode = st.selectbox("اختر نوع الإبداع اليوم:", [
        "📸 توليد صور احترافية (Imagen 3)", 
        "✍️ مساعد ذكي للنصوص والأوامر"
    ])
    prompt = st.text_area("اكتب الوصف هنا:", placeholder="يمكنك الكتابة بالعربية أو الإنجليزية...")
    submit_button = st.button("بدء التوليد الفوري ✨")

# 4. شاشة النتائج
st.subheader("🖼️ شاشة النتائج")

if submit_button and prompt:
    with st.spinner("جاري المعالجة الفورية عبر خوادم جوجل..."):
        try:
            # --- مسار توليد الصور الرسمي والمستقر من جوجل بدون روابط خارجية ---
            if mode == "📸 توليد صور احترافية (Imagen 3)":
                # استدعاء نموذج الصور الرسمي المباشر من جوجل والمربوط بمفتاحك
                result = client.models.generate_images(
                    model='imagen-3.0-generate-002',
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        output_mime_type="image/jpeg",
                        aspect_ratio="1:1"
                    )
                )
                
                if result and result.generated_images:
                    for generated_image in result.generated_images:
                        image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                        st.image(image, caption="تم التوليد بنجاح بواسطة سيرفر جوجل المباشر! 🚀", use_container_width=True)
                        
                        # زر الحفظ المباشر للهاتف
                        st.download_button(
                            label="⬇️ حفظ الصورة في ملفات هاتفك",
                            data=generated_image.image.image_bytes,
                            file_name="google_ai_image.jpg",
                            mime="image/jpeg"
                        )
                else:
                    st.error("⚠️ لم تقم خوادم جوجل بإرجاع الصورة، يرجى المحاولة مرة أخرى بوصف مختلف.")

            # --- مسار مساعد النصوص المستقر ---
            elif mode == "✍️ مساعد ذكي للنصوص والأوامر":
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                if response.text:
                    st.success("✅ تم توليد النص بنجاح:")
                    st.write(response.text)
                else:
                    st.error("⚠️ لم يتم استلام استجابة، يرجى المحاولة مجدداً.")

        except Exception as e:
            st.error(f"❌ حدث خطأ داخلي من السيرفر: {e}")
