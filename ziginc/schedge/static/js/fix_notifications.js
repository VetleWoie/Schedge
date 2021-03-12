function parse_invitation_list(data) {
    // parses the list of notification into a HTML list
    console.log(data)
    var menus = document.getElementsByClassName(notify_menu_class);
    if (menus) {
        var messages = data.unread_list.map(function (item) {
            message = ""
            if (item.verb === "invite") {
                message += item.actor + " has invited you to join an event:</br>" + item.data.title
                // TODO: add buttons for accept and reject
            }
            if (item.verb === "invite accept") {
                message += item.actor + " has accepted your invite for the event:</br>" + item.data.title    
            }
            eventid = item.data.url
            url = "/event/" + eventid + "/" + "fromnotification/" + item.id
            return '<a href=' + url + '><li>' + message + '</li></a>';
        }).join('')
        console.log(messages)
        for (var i = 0; i < menus.length; i++){
            menus[i].innerHTML = messages;
        }
    }
}
