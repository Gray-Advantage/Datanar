let qrDeleteButtons = document.querySelectorAll(".card-body button[data-bs-target='#deleteRedirect']");

qrDeleteButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    let shortLink = btn.getAttribute("data-bs-short-link");
    document.getElementById("redirectShortLink").setAttribute("value", shortLink);
  });
});