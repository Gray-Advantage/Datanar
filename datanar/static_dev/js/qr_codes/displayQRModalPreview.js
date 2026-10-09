let qrImages = document.querySelectorAll(".card-row img");
let qrButtons = document.querySelectorAll(".card-row button[data-bs-target='#QRPreview']")


function updateModalPreview(img) {
  let qrCodeUrl = img.getAttribute("src");
  let overlay = img.nextElementSibling;
  let downloadLinks = overlay.querySelectorAll("input");
  let svgDownloadUrl = downloadLinks[0].getAttribute("value");
  let jpgDownloadUrl = downloadLinks[1].getAttribute("value");
  let pngDownloadUrl = downloadLinks[2].getAttribute("value");

  let link = img.closest(".card-row").querySelector('a[target="_blank"]');
  document.getElementById("qrRedirect").textContent = link.querySelector("strong").innerHTML;

  document.getElementById("qrBigPreview").setAttribute("src", qrCodeUrl);
  document.getElementById("svgDownloadLink").setAttribute("href", svgDownloadUrl);
  document.getElementById("jpgDownloadLink").setAttribute("href", jpgDownloadUrl);
  document.getElementById("pngDownloadLink").setAttribute("href", pngDownloadUrl);
}


qrImages.forEach(img => {
  img.addEventListener("click", () => {
    updateModalPreview(img);
  });
});

qrButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    let img = btn.closest(".card-row").querySelector("img");
    updateModalPreview(img);
  });
});
