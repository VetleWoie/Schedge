var holder = document.querySelector("[dir]");
var prev_section = "home";
function toggle(new_section) {
    if(document.getElementById(prev_section).classList.contains('nav_btn_selected')){
        document.getElementById(prev_section).classList.remove('nav_btn_selected');
    }
    holder.setAttribute('dir', new_section);
    document.getElementById(new_section).classList.add('nav_btn_selected');
    prev_section = new_section;
}



welcomeelement = document.getElementById("welcome_message")


var adjectives = ["affable", "affectionate", "agreeable", "ambitious", "amiable", "amicable", "amusing", "brave", "bright", "broad-minded", "calm", "careful", "charming", "communicative", "compassionate", "conscientious", "considerate", "convivial", "courageous", "courteous", "creative", "decisive", "determined", "diligent", "diplomatic", "discreet", "dynamic", "easygoing", "emotional", "energetic", "enthusiastic", "exuberant", "fair-minded", "faithful", "fearless", "forceful", "frank", "friendly", "funny", "generous", "gentle", "good", "gregarious", "hard-working", "helpful", "honest", "humorous", "imaginative", "impartial", "independent", "intellectual", "intelligent", "intuitive", "inventive", "kind", "loving", "loyal", "modest", "neat", "nice", "optimistic", "passionate", "patient", "persistent", "pioneering", "philosophical", "placid", "plucky", "polite", "powerful", "practical", "pro-active", "quick-witted", "quiet", "rational", "reliable", "reserved", "resourceful", "romantic", "self-confident", "self-disciplined", "sensible", "sensitive", "sincere", "sociable", "straightforward", "sympathetic", "thoughtful", "tidy", "tough", "unassuming", "understanding", "versatile", "warmhearted", "willing", "witty"]

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
    welcomeelement.innerHTML = text + " "  + first_name;
}

