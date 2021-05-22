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