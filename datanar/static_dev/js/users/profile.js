const submitButton = document.getElementById("submit_button");
const avatar = document.getElementById("avatar");
const idAvatar = document.getElementById("id_avatar");
const idUsername = document.getElementById("id_username");

const avatarClear = document.getElementById("avatar-clear_id");
const deleteAvatar = document.getElementById("delete_avatar");

if (!submitButton) {
  throw new Error("'#submit_button' element was not found in the DOM.");
}

const isSubmitButtonVisible = () => !submitButton.classList.contains("d-none");
const showSubmitButton = () => submitButton.classList.remove("d-none");
const hideSubmitButton = () => submitButton.classList.add("d-none");


if (isSubmitButtonVisible()) {
  hideSubmitButton();
}

idUsername?.addEventListener("input", showSubmitButton);
avatarClear?.addEventListener("change", showSubmitButton);

avatar?.addEventListener("click", () => idAvatar.click());

idAvatar?.addEventListener("change", function () {
  if (this.files && this.files.length > 0) {
    const reader = new FileReader();
    reader.onload = (e) => {
      avatar.src = e.target.result;
    }
    reader.readAsDataURL(this.files[0]);
    showSubmitButton();
  }
});

deleteAvatar?.addEventListener("click", () => {
  avatarClear.checked = true;
  submitButton.click();
});
