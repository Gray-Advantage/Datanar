let blockedDomainDeleteButtons = document.querySelectorAll("button[data-bs-target='#blockedDomainDelete']");

blockedDomainDeleteButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    let id = btn.getAttribute("data-bs-domain-id");
    document.getElementById("blockedDomainId").setAttribute("value", id);
  });
});