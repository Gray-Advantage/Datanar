const qrImages = document.querySelectorAll(".card-row img");
const qrButtons = document.querySelectorAll(".card-row button[data-bs-target='#QRPreview']");


function updateModalPreview(img) {
  if (!img) return;

  const qrCodeUrl = img.getAttribute("src");
  const overlay = img.nextElementSibling;

  if (overlay) {
    const downloadLinks = overlay.querySelectorAll("input");
    if (downloadLinks.length >= 3) {
      document.getElementById("svgDownloadLink")?.setAttribute("href", downloadLinks[0].value);
      document.getElementById("jpgDownloadLink")?.setAttribute("href", downloadLinks[1].value);
      document.getElementById("pngDownloadLink")?.setAttribute("href", downloadLinks[2].value);
    }
  }

  const cardRow = img.closest(".card-row");
  const strongTag = cardRow?.querySelector('a[target="_blank"] strong');
  const redirectEl = document.getElementById("qrRedirect");

  if (redirectEl && strongTag) {
    redirectEl.textContent = strongTag.textContent.trim();
  }

  document.getElementById("qrBigPreview")?.setAttribute("src", qrCodeUrl || "");
}


qrImages.forEach(img => {
  img.addEventListener("click", () => updateModalPreview(img));
});

qrButtons.forEach(btn => {
  btn.addEventListener(
    "click", () => {
      const img = btn.closest(".card-row")?.querySelector("img");
      updateModalPreview(img);
    }
  );
});
