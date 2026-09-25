import streamlit as st
from google import genai

# إعداد واجهة الصفحة بالمظهر الداكن
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
st.caption("نسخة مستقرة ونظيفة 100% للنصوص والأوامر عبر خوادم Google المعتمدة")

# التحقق من وجود مفتاح الربط الآمن
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

# لوحة التحكم الجانبية
with st.sidebar:
    st.header("🎛️ لوحة التحكم")
    prompt = st.text_area("اكتب سؤالك أو أمرك للذكاء الاصطناعي هنا:", placeholder="اكتب أي شيء بالعربية أو الإنجليزية...")
    submit_button = st.button("إرسال الأمر الآن ✨")

# شاشة النتائج
st.subheader("🖼️ شاشة النتائج")

if submit_button and prompt:
    with st.spinner("جاري المعالجة الفورية عبر خوادم جوجل..."):
        try:
            # استدعاء نموذج جيميناي السريع والمستقر مجاناً بدون قيود
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            if response.text:
                st.success("✅ تم توليد الرد بنجاح:")
                st.write(response.text)
            else:
                st.error("⚠️ لم يتم استلام استجابة، يرجى المحاولة مجدداً.")
        except Exception as e:
            st.error(f"❌ حدث خطأ داخلي من السيرفر: {e}")
