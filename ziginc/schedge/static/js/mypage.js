var holder = document.querySelector("[dir]");
var prev_section = "home";
function toggle(new_section) {
    /**
     * toggle the sections home, host, participant, and friends
     */
    if (document.getElementById(prev_section).classList.contains('nav_btn_selected')) {
        document.getElementById(prev_section).classList.remove('nav_btn_selected');
    }
    holder.setAttribute('dir', new_section);
    document.getElementById(new_section).classList.add('nav_btn_selected');
    prev_section = new_section;
    sessionStorage.setItem("whence", new_section)
}


/* Search  bar stuff */
const searchFocus = document.getElementById('search-focus');
const keys = [
    { keyCode: 'AltLeft', isTriggered: false },
    { keyCode: 'ControlLeft', isTriggered: false },
];

window.addEventListener('keydown', (e) => {
    keys.forEach((obj) => {
        // check if ctrl or alt was pressed
        if (obj.keyCode === e.code) {
            obj.isTriggered = true;
        }
    });

    const shortcutTriggered = keys.filter((obj) => obj.isTriggered).length === keys.length;

    if (shortcutTriggered) {
        searchFocus.focus();
    }
});

window.addEventListener('keyup', (e) => {

    keys.forEach((obj) => {
        // check if ctrl or alt was released
        if (obj.keyCode === e.code) {
            obj.isTriggered = false;
        }
    });
});

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

window.onload = () => {
    /* restore the section where were last time */
    section = sessionStorage.getItem("whence")
    if (section !== null) {
        toggle(section);
    } 
}


welcomeelement = document.getElementById("welcome_message")


var adjectives = ["affable", "agreeable", "ambitious", "amiable", "amicable", "amusing", "brave", "bright", "broad-minded", "calm", "careful", "charming", "conscientious", "considerate", "courageous", "courteous", "creative", "decisive", "determined", "diligent", "diplomatic", "dynamic", "easygoing", "energetic", "enthusiastic", "exuberant", "fair-minded", "fearless", "friendly", "funny", "generous", "gentle", "good", "hard-working", "helpful", "honest", "humorous", "imaginative", "intellectual", "intelligent", "kind", "loving", "neat", "nice", "optimistic", "persistent", "practical", "quick-witted", "rational", "reliable", "sensible", "sincere", "sociable", "thoughtful", "tough", "warmhearted", "witty"]

function put_welcome_message(first_name) {
    /* display a welcome message to the user
    *  contents depend on the time of day as well as a random nice adjective
    */
    var now = new Date();
    var hour = now.getHours();
    var i = Math.floor(Math.random() * adjectives.length);
    var adjective = adjectives[i];
    text = ""
    if (hour >= 5 && hour <= 11) {
        text += "Good morning";
    } else if (hour >= 12 && hour <= 17) {
        text += "Good afternoon"
    } else if (hour >= 18 || hour <= 4) {
        text += "Good evening"
    } else {
        // something went horribly wrong. go with the safe choice.
        text += "Hello"
    }
    welcomeelement.innerHTML = `${text} ${adjective} ${first_name}`;
}

function validateSubmit(message, id) {
    result = confirm(message);
    if (result) {
        $('#' + id).submit();
    }
}