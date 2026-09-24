# Mankino AI Backend

## النماذج المفعلة

- Nano Banana Pro: `gemini-3-pro-image`
- Nano Banana 2: `gemini-3.1-flash-image`
- Veo 3.1: `veo-3.1-generate-preview`
- Gemini Omni Flash: `gemini-omni-1.1-flash`

هذه النماذج تستخدم Google Gemini API. Nano Banana Pro مخصص للصور، بينما Veo 3.1 وGemini Omni Flash مخصصان لتوليد الفيديو.

## تشغيل محليًا

1. ثبّت Node.js 20+.
2. نفّذ `npm install`.
3. انسخ `.env.example` إلى `.env`.
4. ضع مفتاح Google AI Studio في `GEMINI_API_KEY`.
5. نفّذ `npm start`.

## Render

أنشئ Web Service من نفس مستودع GitHub:

- Root Directory: `backend`
- Build Command: `npm install`
- Start Command: `npm start`
- Environment Variable:
  - Key: `GEMINI_API_KEY`
  - Value: مفتاحك السري

لا تضع المفتاح في GitHub أو في ملفات frontend.

بعد الحصول على رابط Render، ضعه في `frontend/app.js` بدل:
`https://YOUR-RENDER-BACKEND.onrender.com`

ثم ارفع مجلد frontend إلى GitHub Pages.
