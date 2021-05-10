var holder = document.querySelector("[dir]");
var prev_section = "home";
function toggle(new_section) {
    if (document.getElementById(prev_section).classList.contains('nav_btn_selected')) {
        document.getElementById(prev_section).classList.remove('nav_btn_selected');
    }
    holder.setAttribute('dir', new_section);
    document.getElementById(new_section).classList.add('nav_btn_selected');
    prev_section = new_section;
}

const searchFocus = document.getElementById('search-focus');
const keys = [
    { keyCode: 'AltLeft', isTriggered: false },
    { keyCode: 'ControlLeft', isTriggered: false },
];

window.addEventListener('keydown', (e) => {
    keys.forEach((obj) => {
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
        if (obj.keyCode === e.code) {
            obj.isTriggered = false;
        }
    });
});

document.addEventListener("submit", (e) => {
    // Store reference to form to make later code easier to read
    const form = e.target;
  
    // Post data using the Fetch API
    fetch(form.action, {
      method: form.method,
      body: new FormData(form),
    }).then((response => {
        response.text().then(txt => {alert(txt)});
        form.reset();
    }));


    // Prevent the default form submit
    e.preventDefault();
  });


welcomeelement = document.getElementById("welcome_message")


var adjectives = ["affable", "agreeable", "ambitious", "amiable", "amicable", "amusing", "brave", "bright", "broad-minded", "calm", "careful", "charming", "conscientious", "considerate", "courageous", "courteous", "creative", "decisive", "determined", "diligent", "diplomatic", "dynamic", "easygoing", "energetic", "enthusiastic", "exuberant", "fair-minded", "fearless", "friendly", "funny", "generous", "gentle", "good", "hard-working", "helpful", "honest", "humorous", "imaginative", "intellectual", "intelligent", "kind", "loving", "neat", "nice", "optimistic", "persistent", "practical", "quick-witted", "rational", "reliable", "sensible", "sincere", "sociable", "thoughtful", "tough", "warmhearted", "witty"]

function put_welcome_message(first_name) {
    var now = new Date();
    var hour = now.getHours();
    console.log(hour)
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

