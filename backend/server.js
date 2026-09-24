import express from "express";
import cors from "cors";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 10000;
const KEY = process.env.GEMINI_API_KEY;

app.use(cors());
app.use(express.json({limit:"30mb"}));

function authHeaders() {
  return {"Content-Type":"application/json","x-goog-api-key":KEY};
}
function requireKey(res) {
  if (!KEY) { res.status(500).json({error:"GEMINI_API_KEY غير مضبوط في الخادم."}); return false; }
  return true;
}
function stripDataUrl(x) {
  return String(x || "").replace(/^data:.*?;base64,/,"");
}
function videoFromInteraction(j) {
  const steps = j?.steps || [];
  for (const step of steps) {
    for (const c of (step.content || [])) {
      if (c.type === "video" && c.data) return c.data;
    }
  }
  return j?.output_video?.data || null;
}

app.get("/", (req,res)=>res.json({ok:true,name:"Mankino AI Backend"}));

app.post("/api/generate-image", async (req,res)=>{
  if (!requireKey(res)) return;
  try {
    const {model="gemini-3-pro-image",prompt,image,aspectRatio="9:16",imageSize="2K"} = req.body;
    if (!image?.data) return res.status(400).json({error:"أرسل صورة مرجعية."});
    if (!["gemini-3-pro-image","gemini-3.1-flash-image"].includes(model))
      return res.status(400).json({error:"نموذج الصورة غير مدعوم."});

    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;
    const body = {
      contents:[{
        role:"user",
        parts:[
          {inline_data:{mime_type:image.mimeType || "image/jpeg",data:stripDataUrl(image.data)}},
          {text:`${prompt}\nUse the uploaded clothing/model image as a visual reference. Preserve the clothing design, colors, material and important details. Create a professional fashion image.`}
        ]
      }],
      generationConfig:{
        responseModalities:["IMAGE"],
        imageConfig:{aspectRatio,imageSize}
      }
    };
    const r = await fetch(url,{method:"POST",headers:authHeaders(),body:JSON.stringify(body)});
    const j = await r.json();
    if (!r.ok) return res.status(r.status).json({error:j.error?.message || "Google image API error",details:j});
    const parts = j?.candidates?.[0]?.content?.parts || [];
    const part = parts.find(p=>p.inlineData || p.inline_data);
    const img = part?.inlineData || part?.inline_data;
    if (!img?.data) return res.status(502).json({error:"لم يرجع النموذج صورة.",details:j});
    res.json({mimeType:img.mimeType || img.mime_type || "image/png",data:img.data});
  } catch(e) { res.status(500).json({error:e.message}); }
});

app.post("/api/generate-video", async (req,res)=>{
  if (!requireKey(res)) return;
  try {
    const {model="veo-3.1-generate-preview",prompt,image,aspectRatio="9:16",resolution="720p"} = req.body;
    if (!image?.data) return res.status(400).json({error:"أرسل صورة مرجعية."});

    if (model === "gemini-omni-1.1-flash") {
      const body = {
        model,
        input:[
          {type:"image",data:stripDataUrl(image.data),mime_type:image.mimeType || "image/jpeg"},
          {type:"text",text:`${prompt}\nCreate a polished fashion video from the reference image. Keep the clothing design and appearance consistent.`}
        ],
        response_format:{type:"video",aspect_ratio:aspectRatio,resolution}
      };
      const r = await fetch("https://generativelanguage.googleapis.com/v1beta/interactions",{method:"POST",headers:authHeaders(),body:JSON.stringify(body)});
      const j = await r.json();
      if (!r.ok) return res.status(r.status).json({error:j.error?.message || "Gemini Omni error",details:j});
      const data = videoFromInteraction(j);
      if (!data) return res.status(502).json({error:"Gemini Omni لم يرجع فيديو.",details:j});
      return res.json({data});
    }

    if (model === "veo-3.1-generate-preview") {
      const body = {
        instances:[{
          prompt:`${prompt}\nUse the supplied image as the starting visual reference. Preserve the clothing and model appearance as much as possible.`,
          image:{bytesBase64Encoded:stripDataUrl(image.data),mimeType:image.mimeType || "image/jpeg"}
        }],
        parameters:{aspectRatio, resolution, durationSeconds:8}
      };
      const r = await fetch("https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-generate-preview:predictLongRunning",
        {method:"POST",headers:authHeaders(),body:JSON.stringify(body)});
      let op = await r.json();
      if (!r.ok) return res.status(r.status).json({error:op.error?.message || "Veo start error",details:op});

      const name = op.name;
      if (!name) return res.status(502).json({error:"لم يرجع Veo عملية توليد.",details:op});

      for (let i=0;i<36;i++) {
        await new Promise(x=>setTimeout(x,10000));
        const rr = await fetch(`https://generativelanguage.googleapis.com/v1beta/${name}`,{headers:{"x-goog-api-key":KEY}});
        op = await rr.json();
        if (op.done) break;
      }
      if (!op.done) return res.status(504).json({error:"استغرق Veo وقتًا أطول من الحد المسموح. أعد المحاولة."});
      if (op.error) return res.status(502).json({error:op.error.message || "Veo generation failed",details:op});

      const uri =
        op.response?.generateVideoResponse?.generatedSamples?.[0]?.video?.uri ||
        op.response?.generateVideoResponse?.generatedVideos?.[0]?.video?.uri;

      if (!uri) return res.status(502).json({error:"لم يتم العثور على ملف الفيديو.",details:op});

      const vr = await fetch(uri,{headers:{"x-goog-api-key":KEY}});
      if (!vr.ok) return res.status(502).json({error:"تعذر تنزيل فيديو Veo من Google."});
      const buf = Buffer.from(await vr.arrayBuffer());
      return res.json({data:buf.toString("base64")});
    }

    return res.status(400).json({error:"نموذج الفيديو غير مدعوم."});
  } catch(e) { res.status(500).json({error:e.message}); }
});

app.listen(PORT,()=>console.log(`Mankino AI backend running on port ${PORT}`));
