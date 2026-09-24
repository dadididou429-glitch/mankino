# Mankino AI Backend

## النماذج المفعلة

- **Nano Banana Pro:** `gemini-3-pro-image`
- **Nano Banana 2:** `gemini-3.1-flash-image`
- **Veo 3.1:** `veo-3.1-generate-preview`
- **Gemini Omni Flash:** `gemini-omni-1.1-flash`

هذه النماذج تستخدم Google Gemini API الرسمي فقط.

## تشغيل محليًا

1. ثبّت Node.js 20+.
2. نفّذ `npm install`.
3. انسخ `.env.example` إلى `.env`.
4. ضع مفتاح Google AI Studio في `GEMINI_API_KEY`.
5. نفّذ `npm start`.

## Render

أنشئ Web Service من نفس مستودع GitHub:

- **Root Directory:** `backend`
- **Build Command:** `npm install`
- **Start Command:** `npm start`
- **Environment Variable:**
  - Key: `GEMINI_API_KEY`
  - Value: مفتاحك السري من Google AI Studio

**لا تضع المفتاح في GitHub أو في ملفات Frontend.**

بعد النشر، تأكد أن الواجهة تشير إلى:
`https://mankino.onrender.com`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | حالة الخدمة + النماذج |
| GET | `/health` | فحص وجود المفتاح |
| POST | `/api/generate-image` | توليد صورة أزياء |
| POST | `/api/generate-video` | توليد فيديو أزياء |

### Body مثال (صورة)

```json
{
  "model": "gemini-3.1-flash-image",
  "prompt": "عارضة أزياء ترتدي هذا الفستان...",
  "image": { "mimeType": "image/jpeg", "data": "<base64>" },
  "aspectRatio": "9:16",
  "imageSize": "2K"
}
```

### Body مثال (فيديو)

```json
{
  "model": "veo-3.1-generate-preview",
  "prompt": "فيديو أزياء سينمائي...",
  "image": { "mimeType": "image/jpeg", "data": "<base64>" },
  "aspectRatio": "9:16",
  "resolution": "720p"
}
```
