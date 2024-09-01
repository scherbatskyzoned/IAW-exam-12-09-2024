function checkPassword(e) {
  let password = document.getElementById('passwordInput').value;
  let checkPassword = document.getElementById('passwordCheckInput').value;
  let errorMessage = document.getElementById('error-message');
  let icon = document.getElementById('exclamation');
  let upperCaseLetters = /[A-Z]/g;
  let lowerCaseLetters = /[a-z]/g;
  let numbers = /[0-9]/g;

  if (password.length < 8) {
    errorMessage.textContent = "La password deve essere di almeno 8 caratteri."
    icon.style.display = "inline";
    e.preventDefault();
  }
  else if (!password.match(upperCaseLetters) || !password.match(lowerCaseLetters) ||
           !password.match(numbers)) {
    errorMessage.textContent = "Scegli una password più sicura. Prova a utilizzare una combinazione di lettere e numeri."
    icon.style.display = "inline";
    e.preventDefault();
  }
  else if (password != checkPassword) {
    errorMessage.textContent = "Le password non corrispondono. Riprova.";
    icon.style.display = "inline";
    e.preventDefault();
  }
}