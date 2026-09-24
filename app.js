const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const uploadEmpty = document.getElementById("uploadEmpty");
const selectedStatus = document.getElementById("selectedStatus");
const prompt = document.getElementById("prompt");
const counter = document.getElementById("counter");
const generateBtn = document.getElementById("generateBtn");
const toast = document.getElementById("toast");

let mode = "image";
let selectedModel = "";

function showToast(message){
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(window.__toast);
  window.__toast = setTimeout(()=>toast.classList.remove("show"), 2300);
}

imageInput.addEventListener("change", e => {
  const file = e.target.files?.[0];
  if(!file) return;
  const url = URL.createObjectURL(file);
  preview.src = url;
  preview.hidden = false;
  uploadEmpty.hidden = true;
  selectedStatus.textContent = file.name;
  showToast("تم اختيار الصورة");
});

prompt.addEventListener("input", () => {
  counter.textContent = `${prompt.value.length}/500`;
});

document.querySelectorAll(".mode").forEach(btn=>{
  btn.addEventListener("click",()=>{
    document.querySelectorAll(".mode").forEach(x=>x.classList.remove("active"));
    btn.classList.add("active");
    mode = btn.dataset.mode;
    generateBtn.innerHTML = mode === "video" ? "<span>✦</span> ابدأ توليد الفيديو" : "<span>✦</span> ابدأ توليد الصورة";
  });
});

document.querySelectorAll(".model-card").forEach(card=>{
  card.addEventListener("click",()=>{
    selectedModel = card.dataset.model;
    document.querySelectorAll(".model-card").forEach(x=>x.style.outline="none");
    card.style.outline = "2px solid #a855f7";
    showToast(`تم اختيار العارضة: ${selectedModel}`);
  });
});

document.getElementById("imageBtn").onclick = ()=>{
  document.querySelector(".workspace").scrollIntoView({behavior:"smooth"});
  document.querySelector('[data-mode="image"]').click();
};
document.getElementById("videoBtn").onclick = ()=>{
  document.querySelector(".workspace").scrollIntoView({behavior:"smooth"});
  document.querySelector('[data-mode="video"]').click();
};
document.getElementById("modelsBtn").onclick = ()=>{
  document.querySelector(".models-section").scrollIntoView({behavior:"smooth"});
};
document.getElementById("allModels").onclick = ()=>{
  document.querySelector(".models-section").scrollIntoView({behavior:"smooth"});
};
document.getElementById("menuBtn").onclick = ()=>showToast("القائمة ستكون متاحة في النسخة التالية");
document.getElementById("galleryBtn").onclick = ()=>showToast("المعرض سيكون متاحًا بعد ربط التخزين");

generateBtn.onclick = ()=>{
  if(!imageInput.files?.[0]){
    showToast("اختر صورة أولًا");
    return;
  }
  showToast(mode === "video" ? "جاهز لربط توليد الفيديو بمحرك الذكاء الاصطناعي" : "جاهز لربط توليد الصورة بمحرك الذكاء الاصطناعي");
};

if("serviceWorker" in navigator){
  window.addEventListener("load", ()=>navigator.serviceWorker.register("sw.js").catch(()=>{}));
}
