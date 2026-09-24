# مانكينو AI v3

نسخة جاهزة لربط واجهة مانكينو بخوادم Google Gemini API.

## ما الذي تمت إضافته؟

### الصور
- Nano Banana Pro (`gemini-3-pro-image`)
- Nano Banana 2 (`gemini-3.1-flash-image`)

### الفيديو
- Veo 3.1 (`veo-3.1-generate-preview`)
- Gemini Omni Flash (`gemini-omni-1.1-flash`)

الواجهة تسمح برفع صورة الملابس/الموديل، كتابة وصف، اختيار المحرك، ثم توليد صورة أو فيديو.

## مهم جدًا

مفتاح Google API لا يوضع في GitHub Pages. يوضع فقط كمتغير بيئة في الـBackend (Render مثلًا).

## البنية

- `frontend/` — يرفع إلى GitHub Pages.
- `backend/` — ينشر كـ Render Web Service.

## ملاحظة

تكلفة الاستخدام والحدود تعتمد على حساب Google/مشروع Gemini API وخطة Google الحالية.
