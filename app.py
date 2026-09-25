import streamlit as st
from google import genai
import requests

# 1. إعداد واجهة الصفحة وتفعيل المظهر الداكن الفخم
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
st.caption("النسخة الرسمية المستقرة والمجانية بالكامل لعام 2026")

# 2. التحقق من وجود مفتاح جوجل في الإعدادات لتشغيل النصوص
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

# 4. شاشة عرض النتائج
st.subheader("🖼️ شاشة النتائج")

if submit_button and prompt:
    with st.spinner("جاري التوليد الفوري..."):
        try:
            # استخدام ذكاء جوجل لترجمة النص في الخلفية لضمان دقة الصورة وحل مشاكل الحروف العربية
            try:
                translation = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"Translate this prompt into a clean English description for image generation, output ONLY the translated text: {prompt}",
                )
                english_prompt = translation.text.strip() if translation.text else prompt
            except Exception:
                english_prompt = prompt

            # --- مسار توليد الصور المجاني المستقر بنسبة 100% ---
            if mode == "📸 توليد صور احترافية (Imagen 3)":
                # استخدام محرك رسوم فوري ومفتوح لتفادي قيود جوجل المدفوعة
                cleaned_prompt = english_prompt.replace(" ", "-")
                IMAGE_URL = f"https://pollinations.ai{cleaned_prompt}?width=1024&height=1024&nologo=true"
                
                response = requests.get(IMAGE_URL, timeout=30)
                if response.status_code == 200:
                    st.image(response.content, caption="تم التوليد بنجاح! 🚀", use_container_width=True)
                    
                    # زر حفظ الصورة مباشرة في الهاتف
                    st.download_button(
                        label="⬇️ حفظ الصورة في ملفات هاتفك",
                        data=response.content,
                        file_name="ai_image.jpg",
                        mime="image/jpeg"
                    )
                else:
                    st.error("⚠️ الخادم مشغول حالياً، يرجى إعادة المحاولة.")

            # --- مسار مساعد النصوص المستقر والمجاني من جوجل ---
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
            st.error(f"❌ حدث خطأ: {e}")
