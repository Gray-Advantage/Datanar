const copyTextFields = document.querySelectorAll('.copy-text-field');

copyTextFields.forEach(field => {
  field.addEventListener("click", () => {
    const textToCopy = field.getAttribute("data-link");
    navigator.clipboard.writeText(textToCopy).then(() => { });
  });
});
