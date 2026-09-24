const API_BASE = "https://mankino.onrender.com";

// الافتراضي: الأسرع والأقوى توازنًا (Nano Banana 2)
let imageModel = "gemini-3.1-flash-image";
let videoModel = "veo-3.1-generate-preview";
let selectedFile = null;
let resultUrl = null;

const $ = (id) => document.getElementById(id);
const status = (t) => ($("status").textContent = t);

$("imageInput").addEventListener("change", (e) => {
  selectedFile = e.target.files[0];
  if (!selectedFile) return;
  $("fileName").textContent = selectedFile.name;
  const r = new FileReader();
  r.onload = () => {
    $("preview").src = r.result;
    $("preview").classList.remove("hidden");
  };
  r.readAsDataURL(selectedFile);
});

document.querySelectorAll("[data-image-model]").forEach((b) => {
  b.onclick = () => {
    document.querySelectorAll("[data-image-model]").forEach((x) =>
      x.classList.remove("active")
    );
    b.classList.add("active");
    imageModel = b.dataset.imageModel;
  };
});

document.querySelectorAll("[data-video-model]").forEach((b) => {
  b.onclick = () => {
    document.querySelectorAll("[data-video-model]").forEach((x) =>
      x.classList.remove("active")
    );
    b.classList.add("active");
    videoModel = b.dataset.videoModel;
  };
});

function apiReady() {
  if (API_BASE.includes("YOUR-RENDER")) {
    alert("ضع رابط Backend الخاص بك في app.js.");
    return false;
  }
  return true;
}

function dataUrlParts(dataUrl) {
  const m = dataUrl.match(/^data:(.*?);base64,(.*)$/);
  if (!m) throw new Error("صيغة الصورة غير مدعومة");
  return { mimeType: m[1], data: m[2] };
}

function setResult(kind, dataUrl, filename) {
  $("resultCard").classList.remove("hidden");
  $("resultImage").classList.add("hidden");
  $("resultVideo").classList.add("hidden");
  $("downloadBtn").classList.remove("hidden");

  if (resultUrl && resultUrl.startsWith("blob:")) {
    URL.revokeObjectURL(resultUrl);
  }

  if (kind === "image") {
    $("resultImage").src = dataUrl;
    $("resultImage").classList.remove("hidden");
    $("downloadBtn").href = dataUrl;
    $("downloadBtn").download = filename || "mankino-image.png";
    resultUrl = dataUrl;
  } else {
    const base64 = dataUrl.includes(",") ? dataUrl.split(",")[1] : dataUrl;
    const bytes = Uint8Array.from(atob(base64), (c) => c.charCodeAt(0));
    const blob = new Blob([bytes], { type: "video/mp4" });
    resultUrl = URL.createObjectURL(blob);
    $("resultVideo").src = resultUrl;
    $("resultVideo").classList.remove("hidden");
    $("downloadBtn").href = resultUrl;
    $("downloadBtn").download = filename || "mankino-video.mp4";
  }
}

async function fileToDataUrl(file) {
  return await new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(r.result);
    r.onerror = reject;
    r.readAsDataURL(file);
  });
}

// ضغط الصورة قبل الإرسال لتسريع الرفع والتوليد
async function compressImage(file, maxSide = 1280, quality = 0.85) {
  if (!file.type.startsWith("image/")) return fileToDataUrl(file);
  const dataUrl = await fileToDataUrl(file);
  return await new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      let { width, height } = img;
      if (width > maxSide || height > maxSide) {
        if (width > height) {
          height = Math.round((height * maxSide) / width);
          width = maxSide;
        } else {
          width = Math.round((width * maxSide) / height);
          height = maxSide;
        }
      }
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0, width, height);
      resolve(canvas.toDataURL("image/jpeg", quality));
    };
    img.onerror = () => resolve(dataUrl);
    img.src = dataUrl;
  });
}

$("imageBtn").onclick = async () => {
  if (!selectedFile || !apiReady()) return;

  const prompt =
    $("prompt").value.trim() ||
    "Create a premium photorealistic fashion editorial image using the clothing reference. Adult fashion model, natural fit, realistic fabric, studio lighting.";

  $("imageBtn").disabled = true;
  status("جارٍ تجهيز الصورة…");

  try {
    const compressed = await compressImage(selectedFile);
    const ref = dataUrlParts(compressed);

    // Pro = جودة أعلى (2K) | Flash = سرعة أعلى (1K)
    const imageSize = imageModel === "gemini-3-pro-image" ? "2K" : "1K";

    status(
      imageModel.includes("flash")
        ? "توليد سريع (Nano Banana 2)…"
        : "توليد عالي الجودة (Pro)…"
    );

    const res = await fetch(API_BASE + "/api/generate-image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: imageModel,
        prompt,
        image: ref,
        aspectRatio: "9:16",
        imageSize,
      }),
    });

    const j = await res.json();
    if (!res.ok) throw new Error(j.error || "فشل توليد الصورة");

    setResult(
      "image",
      "data:" + (j.mimeType || "image/png") + ";base64," + j.data,
      "mankino-nano-banana.png"
    );
    status("تم التوليد ✓");
  } catch (e) {
    status("حدث خطأ");
    alert(e.message);
  } finally {
    $("imageBtn").disabled = false;
  }
};

$("videoBtn").onclick = async () => {
  if (!selectedFile || !apiReady()) return;

  const prompt =
    $("prompt").value.trim() ||
    "Premium fashion video. Adult fashion model wearing the clothing naturally, realistic fabric motion, elegant walk, cinematic camera movement, studio-quality lighting.";

  $("videoBtn").disabled = true;
  status("جارٍ توليد الفيديو… قد يستغرق دقائق");

  try {
    const compressed = await compressImage(selectedFile, 1024, 0.8);
    const ref = dataUrlParts(compressed);

    const res = await fetch(API_BASE + "/api/generate-video", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: videoModel,
        prompt,
        image: ref,
        aspectRatio: $("ratio").value,
        resolution: $("resolution").value,
      }),
    });

    const j = await res.json();
    if (!res.ok) throw new Error(j.error || "فشل توليد الفيديو");

    setResult("video", "data:video/mp4;base64," + j.data, "mankino-video.mp4");
    status("تم توليد الفيديو ✓");
  } catch (e) {
    status("حدث خطأ");
    alert(e.message);
  } finally {
    $("videoBtn").disabled = false;
  }
};

$("saveBtn").onclick = () => {
  if ($("downloadBtn").classList.contains("hidden")) return;
  $("downloadBtn").click();
};
