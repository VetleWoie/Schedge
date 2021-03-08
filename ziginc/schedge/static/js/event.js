var x = document.getElementById("loc");
var button = document.getElementById("curlocbutton");

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, errorCallBack);
    } else {
        x.value = "Geolocation is not supported by this browser.";
    }
}

function showPosition(position) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            getPlace(xmlHttp.responseText);
        } else {
            console.log(xmlHttp.status);
        }
    }
    var url = "https://nominatim.openstreetmap.org/reverse?lat=" + position.coords.latitude + "&lon=" + position.coords.longitude
    xmlHttp.open("GET", url, true); // true for asynchronous 
    xmlHttp.send(null);
}

function getPlace(response) {
    parser = new DOMParser();
    var xmlDoc = parser.parseFromString(response, "text/xml");
    x.value = xmlDoc.getElementsByTagName("result")[0].childNodes[0].nodeValue;
}

function errorCallBack(error) {
    button.className = "invalid";
}