const qrDeleteButtons = document.querySelectorAll(
  ".card-body button[data-bs-target='#deleteRedirect']"
);
const redirectInput = document.getElementById("redirectShortLink");

qrDeleteButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    const shortLink = btn.getAttribute("data-bs-short-link");
    if (redirectInput) {
      redirectInput.value = shortLink;
    }
  });
});