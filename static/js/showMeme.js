const link = document.querySelector(".meme");
const img = document.getElementById("meme-img");
link.addEventListener('click', function () {
  if (img.style.display === "block") {
    img.style.display = "none";
  }
  else {
    img.style.display = "block";
  }
})