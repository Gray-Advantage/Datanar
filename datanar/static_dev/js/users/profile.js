submit_button = document.getElementById("submit_button");

if (!document.getElementById("submit_button").classList.contains("d-none")) {
  submit_button.classList.add("d-none");
}

document.getElementById("avatar").addEventListener("click", function () {
  document.getElementById("id_avatar").click();
});

document.getElementById("id_avatar").addEventListener("change", function () {
  if (this.files && this.files.length > 0) {
    let reader = new FileReader();
    reader.onload = function (e) {
      document.getElementById("avatar").src = e.target.result;
    }
    reader.readAsDataURL(this.files[0]);
    submit_button.classList.remove("d-none");
  }
});

document.getElementById("avatar-clear_id")?.addEventListener("change", () => {
  submit_button.classList.remove("d-none");
});

document.getElementById("id_username").addEventListener("input", () => {
  submit_button.classList.remove("d-none")
});

document.getElementById("delete_avatar")?.addEventListener("click", () => {
  document.getElementById("avatar-clear_id").setAttribute("checked", "true");
  submit_button.click();
});