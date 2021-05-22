// all the forms where we don't redirect on submit
silent_forms = document.getElementsByClassName("silent-form")

for (var i = 0; i < silent_forms.length; i++) {
    // add the submit listener function to all the forms
    silent_forms[i].addEventListener("submit", silent_submit, false);
}


function silent_submit(e) {
    /**
     * silent submit submits a form, but does not redirect
     * It refreshes if response code is 200
     * otherwise display the error in an alert
     */

    // Store reference to form to make later code easier to read
    const form = e.target;

    // Post data using the fetch
    fetch(form.action, {
        method: form.method,
        body: new FormData(form),
    }).then((response => {
        if (!response.ok) {
            // something went wrong, display the response
            response.text().then(txt => { alert(txt) });
            // dont refresh
            e.preventDefault()
        } else {
            // refresh
            window.location.reload()
        }
    }));


    // Prevent the default form submit
    e.preventDefault();
}

function validateSubmit(message, id) {
    result = confirm(message);
    if (result) {
        $('#' + id).submit();
    }
}