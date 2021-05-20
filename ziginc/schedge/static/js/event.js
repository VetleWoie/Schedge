var x = document.getElementById("id_location");
var button = document.getElementById("curlocbutton");
var loc_errmsg = document.getElementById("loc-err-msg")
var loc_div = document.getElementById("loc-div")

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
    button.classList.add(["invalid"]);
    loc_div.classList.add(["errormsg"]);

    loc_errmsg.className = "errormsgtext"
    loc_errmsg.innerHTML = "Enable location services to use this feature"
}

function validateSubmit(message, id) {
    result = confirm(message);
    if (result) {
        $('#' + id).submit();
    }
}


var holder = document.querySelector("[dir]");
var prev_section = "overlapTS";
function tmslotToggle(new_section) {
    if (document.getElementById(prev_section).classList.contains('folder_active')) {
        document.getElementById(prev_section).classList.remove('folder_active');
        document.getElementById(prev_section).classList.add('folder_unactive');
    }
    holder.setAttribute('dir', new_section);
    document.getElementById(new_section).classList.remove('folder_unactive');
    document.getElementById(new_section).classList.add('folder_active');
    prev_section = new_section;
}


// Source: https://www.tutorialrepublic.com/codelab.php?topic=bootstrap&file=accordion-with-plus-minus-icon

$(document).ready(function(){
    // Add minus icon for collapse element which is open by default
    $(".collapse.show").each(function(){
        $(this).prev(".card-header").find(".fa").addClass("fa-minus").removeClass("fa-plus");
    });
    
    // Toggle plus minus icon on show hide of collapse element
    $(".collapse").on('show.bs.collapse', function(){
        $(this).prev(".card-header").find(".fa").removeClass("fa-plus").addClass("fa-minus");
    }).on('hide.bs.collapse', function(){
        $(this).prev(".card-header").find(".fa").removeClass("fa-minus").addClass("fa-plus");
    });
});