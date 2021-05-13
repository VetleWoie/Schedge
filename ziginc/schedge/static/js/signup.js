let checkbox = document.getElementById('check')
let submit = document.getElementById('signupbtn')

// Enable the user to sign up only after the checkbox have been clicked.
function checkbox_clicked(){
    console.log("function called");
    submit.disabled = !checkbox.checked;
}

// update state of sign up button on page load
window.onload = checkbox_clicked;