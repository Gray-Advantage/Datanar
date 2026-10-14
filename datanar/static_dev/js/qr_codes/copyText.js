const copyTextFields = document.querySelectorAll(".copy-text-field");

copyTextFields.forEach(field => {
  field.addEventListener("click", () => {
    const textToCopy = field.dataset.link;
    if (!textToCopy) return;

    navigator.clipboard.writeText(textToCopy)
      .catch(err => {
        console.error("Error copying text: ", err);
      });
  });
});
