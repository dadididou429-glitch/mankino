import express from "express";
import cors from "cors";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 10000;
const KEY = process.env.GEMINI_API_KEY;

app.use(cors());
app.use(express.json({ limit: "30mb" }));

const ALLOWED_IMAGE_MODELS = ["gemini-3-pro-image", "gemini-3.1-flash-image"];
const ALLOWED_VIDEO_MODELS = ["veo-3.1-generate-preview", "gemini-omni-1.1-flash"];
const MAX_IMAGE_BYTES = 20 * 1024 * 1024;

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "x-goog-api-key": KEY,
  };
}

function requireKey(res) {
  if (!KEY || !String(KEY).trim()) {
    res.status(500).json({
      error: "GEMINI_API_KEY غير مضبوط في Environment Variables على Render.",
    });
    return false;
  }
  return true;
}

function stripDataUrl(x) {
  return String(x || "").replace(/^data:.*?;base64,/, "");
}

function estimateBase64Size(b64) {
  const len = String(b64 || "").length;
  return Math.ceil((len * 3) / 4);
}

function videoFromInteraction(j) {
  const steps = j?.steps || [];
  for (const step of steps) {
    for (const c of step.content || []) {
      if (c.type === "video" && c.data) return c.data;
    }
  }
  if (j?.output_video?.data) return j.output_video.data;
  if (j?.outputs) {
    for (const o of j.outputs) {
      if (o.type === "video" && o.data) return o.data;
    }
  }
  return null;
}

function mapGoogleError(status, body) {
  const msg =
    body?.error?.message ||
    (typeof body?.error === "string" ? body.error : "") ||
    "";
  if (status === 400) {
    if (/API key|api_key|invalid|INVALID_ARGUMENT/i.test(msg))
      return "مفتاح API غير صالح أو منتهي. تحقق من GEMINI_API_KEY في Render.";
    if (/model|not found|unsupported|NOT_FOUND/i.test(msg))
      return "النموذج غير متاح أو غير مدعوم لهذا الحساب.";
    if (/image|size|too large|payload|RESOURCE_EXHAUSTED/i.test(msg))
      return "الصورة كبيرة جدًا أو صيغتها غير مدعومة. جرّب صورة أصغر.";
  }
  if (status === 401 || status === 403)
    return "مفتاح API غير مصرح به أو غير صالح.";
  if (status === 429)
    return "تم تجاوز حد الطلبات. انتظر قليلًا ثم أعد المحاولة.";
  if (status === 503 || status === 500)
    return "خدمة Google غير متاحة مؤقتًا. أعد المحاولة لاحقًا.";
  return msg || "خطأ من Google API.";
}

app.get("/", (req, res) => {
  res.json({
    ok: true,
    name: "Mankino AI Backend",
    models: {
      image: ALLOWED_IMAGE_MODELS,
      video: ALLOWED_VIDEO_MODELS,
    },
  });
});

app.get("/health", (req, res) => {
  res.json({
    ok: true,
    hasKey: Boolean(KEY && String(KEY).trim()),
  });
});

app.post("/api/generate-image", async (req, res) => {
  if (!requireKey(res)) return;

  try {
    const {
      model = "gemini-3.1-flash-image",
      prompt,
      image,
      aspectRatio = "9:16",
      imageSize = "1K",
    } = req.body || {};

    if (!image?.data) {
      return res.status(400).json({ error: "أرسل صورة مرجعية (ملابس أو موديل)." });
    }

    if (!ALLOWED_IMAGE_MODELS.includes(model)) {
      return res.status(400).json({
        error: "نموذج الصورة غير مدعوم.",
        allowed: ALLOWED_IMAGE_MODELS,
      });
    }

    const rawB64 = stripDataUrl(image.data);
    if (estimateBase64Size(rawB64) > MAX_IMAGE_BYTES) {
      return res.status(413).json({
        error: "الصورة كبيرة جدًا. قلّل حجمها ثم أعد المحاولة.",
      });
    }

    const fashionPrompt = [
      prompt ||
        "Create a premium photorealistic fashion editorial image using the clothing reference.",
      "Use the uploaded clothing/model image as a visual reference.",
      "Preserve the clothing design, colors, patterns, material, texture and important details as accurately as possible.",
      "Create a realistic adult fashion model wearing the clothes naturally.",
      "Professional studio lighting, high quality fashion photography.",
    ].join(" ");

    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;
    const body = {
      contents: [
        {
          role: "user",
          parts: [
            {
              inline_data: {
                mime_type: image.mimeType || "image/jpeg",
                data: rawB64,
              },
            },
            { text: fashionPrompt },
          ],
        },
      ],
      generationConfig: {
        responseModalities: ["IMAGE"],
        imageConfig: {
          aspectRatio,
          imageSize,
        },
      },
    };

    const r = await fetch(url, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(body),
    });

    const j = await r.json().catch(() => ({}));

    if (!r.ok) {
      return res.status(r.status).json({
        error: mapGoogleError(r.status, j),
        details: j?.error || j,
      });
    }

    const parts = j?.candidates?.[0]?.content?.parts || [];
    const part = parts.find((p) => p.inlineData || p.inline_data);
    const img = part?.inlineData || part?.inline_data;

    if (!img?.data) {
      return res.status(502).json({
        error:
          "لم يرجع النموذج صورة. قد يكون الطلب مرفوضًا من سياسة المحتوى أو النموذج غير متاح.",
        details: j,
      });
    }

    res.json({
      mimeType: img.mimeType || img.mime_type || "image/png",
      data: img.data,
    });
  } catch (e) {
    console.error("generate-image error:", e);
    res.status(500).json({ error: e.message || "خطأ داخلي في توليد الصورة." });
  }
});

app.post("/api/generate-video", async (req, res) => {
  if (!requireKey(res)) return;

  try {
    const {
      model = "veo-3.1-generate-preview",
      prompt,
      image,
      aspectRatio = "9:16",
      resolution = "720p",
    } = req.body || {};

    if (!image?.data) {
      return res.status(400).json({ error: "أرسل صورة مرجعية (ملابس أو موديل)." });
    }

    if (!ALLOWED_VIDEO_MODELS.includes(model)) {
      return res.status(400).json({
        error: "نموذج الفيديو غير مدعوم.",
        allowed: ALLOWED_VIDEO_MODELS,
      });
    }

    const rawB64 = stripDataUrl(image.data);
    if (estimateBase64Size(rawB64) > MAX_IMAGE_BYTES) {
      return res.status(413).json({
        error: "الصورة كبيرة جدًا. قلّل حجمها ثم أعد المحاولة.",
      });
    }

    const fashionPrompt = [
      prompt ||
        "Premium fashion video. Adult fashion model wearing the clothing naturally, realistic fabric motion, elegant walk, cinematic camera movement, studio-quality lighting.",
      "Use the supplied image as the starting visual reference.",
      "Preserve the clothing design, colors, material and appearance as much as possible.",
    ].join(" ");

    if (model === "gemini-omni-1.1-flash") {
      const body = {
        model,
        input: [
          {
            type: "image",
            data: rawB64,
            mime_type: image.mimeType || "image/jpeg",
          },
          { type: "text", text: fashionPrompt },
        ],
        response_format: {
          type: "video",
          aspect_ratio: aspectRatio,
          resolution,
        },
      };

      const r = await fetch(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        {
          method: "POST",
          headers: authHeaders(),
          body: JSON.stringify(body),
        }
      );

      const j = await r.json().catch(() => ({}));

      if (!r.ok) {
        return res.status(r.status).json({
          error: mapGoogleError(r.status, j),
          details: j?.error || j,
        });
      }

      const data = videoFromInteraction(j);
      if (!data) {
        return res.status(502).json({
          error: "Gemini Omni لم يرجع فيديو. قد يكون النموذج غير متاح لحسابك.",
          details: j,
        });
      }

      return res.json({ data, mimeType: "video/mp4" });
    }

    if (model === "veo-3.1-generate-preview") {
      const body = {
        instances: [
          {
            prompt: fashionPrompt,
            image: {
              bytesBase64Encoded: rawB64,
              mimeType: image.mimeType || "image/jpeg",
            },
          },
        ],
        parameters: {
          aspectRatio,
          resolution,
          durationSeconds: 8,
        },
      };

      const startRes = await fetch(
        "https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-generate-preview:predictLongRunning",
        {
          method: "POST",
          headers: authHeaders(),
          body: JSON.stringify(body),
        }
      );

      let op = await startRes.json().catch(() => ({}));

      if (!startRes.ok) {
        return res.status(startRes.status).json({
          error: mapGoogleError(startRes.status, op),
          details: op?.error || op,
        });
      }

      const name = op.name;
      if (!name) {
        return res.status(502).json({
          error: "لم يرجع Veo عملية توليد.",
          details: op,
        });
      }

      const maxPolls = 36;
      for (let i = 0; i < maxPolls; i++) {
        await new Promise((r) => setTimeout(r, 10000));
        const pollRes = await fetch(
          `https://generativelanguage.googleapis.com/v1beta/${name}`,
          { headers: { "x-goog-api-key": KEY } }
        );
        op = await pollRes.json().catch(() => ({}));
        if (op.done) break;
      }

      if (!op.done) {
        return res.status(504).json({
          error:
            "استغرق توليد الفيديو وقتًا أطول من الحد المسموح. أعد المحاولة لاحقًا.",
        });
      }

      if (op.error) {
        return res.status(502).json({
          error: op.error.message || "فشل توليد فيديو Veo.",
          details: op,
        });
      }

      const uri =
        op.response?.generateVideoResponse?.generatedSamples?.[0]?.video?.uri ||
        op.response?.generateVideoResponse?.generatedVideos?.[0]?.video?.uri ||
        op.response?.generatedSamples?.[0]?.video?.uri ||
        op.response?.videos?.[0]?.uri;

      if (!uri) {
        return res.status(502).json({
          error: "لم يتم العثور على رابط ملف الفيديو في رد Veo.",
          details: op,
        });
      }

      const vr = await fetch(uri, {
        headers: { "x-goog-api-key": KEY },
      });

      if (!vr.ok) {
        return res.status(502).json({
          error: "تعذر تنزيل فيديو Veo من Google.",
        });
      }

      const buf = Buffer.from(await vr.arrayBuffer());
      return res.json({
        data: buf.toString("base64"),
        mimeType: "video/mp4",
      });
    }

    return res.status(400).json({ error: "نموذج الفيديو غير مدعوم." });
  } catch (e) {
    console.error("generate-video error:", e);
    res.status(500).json({ error: e.message || "خطأ داخلي في توليد الفيديو." });
  }
});

app.listen(PORT, () => {
  console.log(`Mankino AI backend running on port ${PORT}`);
});
