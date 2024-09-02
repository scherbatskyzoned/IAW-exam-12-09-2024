const toggles = document.querySelectorAll(".field-icon");
const psw = document.querySelectorAll(".password-input");

for (let i = 0; i < toggles.length; i++) {
  toggles[i].addEventListener('click', function () {
    for (let j=0; j < psw.length; j++) {
       // Toggle the type attribute using getAttribute() method
      const type = psw[j].getAttribute('type') === 'password' ? 'text' : 'password';
      psw[j].setAttribute('type', type);
    }
    // Toggle the eye icon
    this.classList.toggle('fa-eye-slash');
    if (toggles.length === 2) { 
      if (i === 0) {
        toggles[i+1].classList.toggle('fa-eye-slash');
      }
      else {
        toggles[i-1].classList.toggle('fa-eye-slash');
      }
    }
  });
};