function checkPassword(e) {
  let password = document.getElementById('passwordInput').value;
  let checkPassword = document.getElementById('passwordCheckInput').value;
  let errorMessage = document.getElementById('error-message');

  console.log(password, checkPassword);
  if (password != checkPassword) {
    errorMessage.textContent = "Le password non corrispondono. Riprova.";
    errorMessage.style.color = "#b3261e";   
    e.preventDefault();
  }
}