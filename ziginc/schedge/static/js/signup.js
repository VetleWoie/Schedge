let checkbox = document.getElementById('check')
let submit = document.getElementById('signupbtn')

// Enable the user to sign up only after the checkbox have been clicked.
function checkbox_clicked(){
    submit.disabled = !submit.disabled
}