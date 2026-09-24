const API_BASE = "https://mankino.onrender.com";

let imageModel = "gemini-3-pro-image";
let videoModel = "veo-3.1-generate-preview";
let selectedFile = null;
let resultUrl = null;

const $ = id => document.getElementById(id);
const status = t => $("status").textContent = t;

$("imageInput").addEventListener("change", e => {
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

document.querySelectorAll("[data-image-model]").forEach(b => {
  b.onclick = () => {
    document.querySelectorAll("[data-image-model]")
      .forEach(x => x.classList.remove("active"));

    b.classList.add("active");
    imageModel = b.dataset.imageModel;
  };
});

document.querySelectorAll("[data-video-model]").forEach(b => {
  b.onclick = () => {
    document.querySelectorAll("[data-video-model]")
      .forEach(x => x.classList.remove("active"));

    b.classList.add("active");
    videoModel = b.dataset.videoModel;
  };
});

function apiReady() {
  if (API_BASE.includes("YOUR-RENDER")) {
    alert("رابط Backend غير مضبوط.");
    return false;
  }

  return true;
}

function dataUrlParts(dataUrl) {
  const m = dataUrl.match(/^data:(.*?);base64,(.*)$/);

  if (!m) {
    throw new Error("صيغة الصورة غير مدعومة");
  }

  return {
    mimeType: m[1],
    data: m[2]
  };
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
    $("downloadBtn").download =
      filename || "mankino-image.png";

    resultUrl = dataUrl;

  } else {
    const bytes = Uint8Array.from(
      atob(dataUrl.split(",")[1]),
      c => c.charCodeAt(0)
    );

    const blob = new Blob(
      [bytes],
      { type: "video/mp4" }
    );

    resultUrl = URL.createObjectURL(blob);

    $("resultVideo").src = resultUrl;
    $("resultVideo").classList.remove("hidden");

    $("downloadBtn").href = resultUrl;
    $("downloadBtn").download =
      filename || "mankino-video.mp4";
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


// ===============================
// توليد الصورة - Nano Banana Pro
// ===============================

$("imageBtn").onclick = async () => {

  if (!selectedFile || !apiReady()) {
    return;
  }

  const prompt =
    $("prompt").value.trim() ||
    "Create a premium photorealistic fashion editorial image using the clothing reference. Adult fashion model, natural fit, realistic fabric, studio lighting.";

  $("imageBtn").disabled = true;

  status("جارٍ توليد الصورة…");

  try {

    const ref = dataUrlParts(
      await fileToDataUrl(selectedFile)
    );

    const res = await fetch(
      API_BASE + "/api/generate-image",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          model: imageModel,
          prompt: prompt,
          image: ref,
          aspectRatio: "9:16",
          imageSize: "2K"
        })
      }
    );

    const j = await res.json();

    if (!res.ok) {
      throw new Error(
        j.error || "فشل توليد الصورة"
      );
    }

    setResult(
      "image",
      "data:" + j.mimeType +
      ";base64," + j.data,
      "mankino-nano-banana.png"
    );

    status("تم توليد الصورة");

  } catch (e) {

    status("حدث خطأ");

    alert(e.message);

  } finally {

    $("imageBtn").disabled = false;

  }
};


// ===============================
// توليد الفيديو - Veo 3.1
// ===============================

$("videoBtn").onclick = async () => {

  if (!selectedFile || !apiReady()) {
    return;
  }

  const prompt =
    $("prompt").value.trim() ||
    "Premium fashion video. Adult fashion model wearing the clothing naturally, realistic fabric motion, elegant walk, cinematic camera movement, studio-quality lighting.";

  $("videoBtn").disabled = true;

  status(
    "جارٍ توليد الفيديو… قد يستغرق عدة دقائق"
  );

  try {

    const ref = dataUrlParts(
      await fileToDataUrl(selectedFile)
    );

    const res = await fetch(
      API_BASE + "/api/generate-video",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          model: videoModel,
          prompt: prompt,
          image: ref,
          aspectRatio: $("ratio").value,
          resolution: $("resolution").value
        })
      }
    );

    const j = await res.json();

    if (!res.ok) {
      throw new Error(
        j.error || "فشل توليد الفيديو"
      );
    }

    setResult(
      "video",
      "data:video/mp4;base64," + j.data,
      "mankino-video.mp4"
    );

    status("تم توليد الفيديو");

  } catch (e) {

    status("حدث خطأ");

    alert(e.message);

  } finally {

    $("videoBtn").disabled = false;

  }
};


// ===============================
// حفظ النتيجة
// ===============================

$("saveBtn").onclick = () => {

  if (
    $("downloadBtn").classList.contains("hidden")
  ) {
    return;
  }

  $("downloadBtn").click();

};
