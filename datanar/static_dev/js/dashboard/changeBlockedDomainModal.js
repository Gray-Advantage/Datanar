let blockedDomainChangeButtons = document.querySelectorAll("button[data-bs-target='#blockedDomainChange']");

blockedDomainChangeButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    let id = btn.getAttribute("data-bs-domain-id");
    let oldRegex = btn.getAttribute("data-bs-domain-regex");
    document.getElementById("blockedDomainIdChange").setAttribute("value", id);
    document.getElementById("blockedDomainRegexOld").setAttribute("value", oldRegex);
  });
});