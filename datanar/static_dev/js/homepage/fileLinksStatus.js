let loader = document.getElementById("fileLinksLoader");

if (loader) {
  let checkStatus = setInterval(() => {
    fetch("/file_status/" + loader.textContent.trim(), { redirect: "manual" })
      .then(response => {
        if (response.status === 202) {
          console.log("Wait!");
        } else {
          clearInterval(checkStatus);
          window.location.href = "/";
        }
      })
  }, 1000);
}