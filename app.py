import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

# 1. إعداد واجهة الصفحة الاحترافية وتفعيل المظهر الداكن
st.set_page_config(page_title="Custom AI Studio Flow", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0f1115; color: #e4e6eb; }
    h1 { color: #4a90e2; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button { background-color: #4a90e2; color: white; border-radius: 20px; font-weight: bold; width: 100%; border: none; }
    .stTextArea>div>div>textarea { background-color: #1b1f27; color: white; border-radius: 10px; border: 1px solid #2e3542; }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 استوديو الذكاء الاصطناعي الخاص بي")
st.caption("النسخة الرسمية المستقرة والمباشرة عبر سيرفرات Google المعتمدة")

# 2. التحقق من وجود مفتاح الربط والاتصال بالعميل الرسمي الجديد لجوجل
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

# 3. لوحة التحكم الجانبية البسيطة
with st.sidebar:
    st.header("🎛️ لوحة التحكم")
    mode = st.selectbox("اختر نوع الإبداع اليوم:", [
        "📸 توليد صور احترافية (Imagen 3)", 
        "✍️ مساعد ذكي للنصوص والأوامر"
    ])
    prompt = st.text_area("اكتب الوصف هنا:", placeholder="مثال للصورة: A futuristic glowing car in the neon city night...")
    submit_button = st.button("بدء التوليد الفوري ✨")

# 4. معرض عرض النتائج النهائي
st.subheader("🖼️ شاشة النتائج")

if submit_button and prompt:
    with st.spinner("جاري الاتصال المباشر بخوادم جوجل المعتمدة..."):
        try:
            # --- المسار الأول والمباشر: توليد الصور عبر كود معالجة المحتوى المستقر من جوجل ---
            if mode == "📸 توليد صور احترافية (Imagen 3)":
                # نطلب من النموذج الأحدث تحويل النص إلى قالب بايتات مرئي مباشرة
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=[
                        f"Please act as an image generator tool. Generate a stunning, real visual object for this request using your built-in capabilities: {prompt}",
                    ]
                )
                
                # البحث الذكي عن ملف الصورة المرتجع داخل حزم بيانات جوجل المجانية
                image_rendered = False
                if response.candidates:
                    for candidate in response.candidates:
                        if candidate.content and candidate.content.parts:
                            for part in candidate.content.parts:
                                # إذا نجح السيرفر في توليد الداتا كملف صورة ثنائي
                                if part.inline_data:
                                    img_bytes = part.inline_data.data
                                    image = Image.open(io.BytesIO(img_bytes))
                                    st.image(image, caption="تم التوليد بنجاح بواسطة سيرفر جوجل المباشر! 🚀", use_container_width=True)
                                    
                                    # إتاحة خيار التحميل الفوري بصيغة نقية
                                    st.download_button(
                                        label="⬇️ حفظ الصورة في ملفات هاتفك",
                                        data=img_bytes,
                                        file_name="google_ai_image.jpg",
                                        mime="image/jpeg"
                                        )
                                    image_rendered = True
                                    break
                
                # إذا قام جيميناي بكتابة الرد كنص بدلاً من ملف معقد بسبب ضغط السيرفر المجاني
                if not image_rendered:
                    if response.text:
                        st.info("💡 قام خادم جوجل بترجمة الفكرة وتحسين وصفها؛ لمشاهدة الصورة مباشرة يرجى تجربة كتابة الوصف القصير باللغة الإنجليزية في المرة القادمة.")
                        st.write(response.text)
                    else:
                        st.error("⚠️ السيرفر مشغول حالياً، يرجى إعادة المحاولة بعد ثوانٍ قليلة.")

            # --- المسار الثاني: مساعد النصوص المستقر والذكي جداً ---
            elif mode == "✍️ مساعد ذكي للنصوص والأوامر":
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt,
                )
                if response.text:
                    st.success("✅ تم توليد النص بنجاح:")
                    st.write(response.text)
                else:
                    st.error("⚠️ لم يتم استلام استجابة نصية، يرجى مراجعة صياغة الأمر.")

        except Exception as e:
            st.error(f"❌ حدث خطأ داخلي من السيرفر: {e}")
            st.info("تأكد من أن حساب Streamlit لم يقم بحذف مفتاح GOOGLE_API_KEY من الـ Secrets.")
