welcomeelement = document.getElementById("welcome_message")


var adjectives = ["affable", "affectionate", "agreeable", "ambitious", "amiable", "amicable", "amusing", "brave", "bright", "broad-minded", "calm", "careful", "charming", "communicative", "compassionate", "conscientious", "considerate", "convivial", "courageous", "courteous", "creative", "decisive", "determined", "diligent", "diplomatic", "discreet", "dynamic", "easygoing", "emotional", "energetic", "enthusiastic", "exuberant", "fair-minded", "faithful", "fearless", "forceful", "frank", "friendly", "funny", "generous", "gentle", "good", "gregarious", "hard-working", "helpful", "honest", "humorous", "imaginative", "impartial", "independent", "intellectual", "intelligent", "intuitive", "inventive", "kind", "loving", "loyal", "modest", "neat", "nice", "optimistic", "passionate", "patient", "persistent", "pioneering", "philosophical", "placid", "plucky", "polite", "powerful", "practical", "pro-active", "quick-witted", "quiet", "rational", "reliable", "reserved", "resourceful", "romantic", "self-confident", "self-disciplined", "sensible", "sensitive", "sincere", "sociable", "straightforward", "sympathetic", "thoughtful", "tidy", "tough", "unassuming", "understanding", "versatile", "warmhearted", "willing", "witty"]

function put_welcome_message(first_name) {
    var now = new Date();
    var hour = now.getHours();
    var i = Math.floor(Math.random() * adjectives.length);
    var adjective = adjectives[i];
    text = ""
    if (hour >= 5 && hour <= 11) {
        text += "good morning";
    } else if (hour >= 12 && hour <= 17) {
        text += "good afternoon"
    } else if (hour >= 18 && hour <= 4) {
        text += "good evening"
    } else {
        // something went horribly wrong. go with the safe choice.
        text += "hello"
    }
    welcomeelement.innerHTML = text + " " + adjective + " " + first_name;
}

