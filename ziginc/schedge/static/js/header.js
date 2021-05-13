var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;



function click_bell() {
    let menus = document.getElementsByClassName(notify_menu_class)

    for (var i = 0; i < menus.length; i++) {
        if (menus[i].classList.contains("hidden-list")) {
            menus[i].classList.remove("hidden-list");
            menus[i].classList.add("visible-list");
        } else {
            menus[i].classList.add("hidden-list");
            menus[i].classList.remove("visible-list");
        }
    }
}


document.addEventListener("DOMContentLoaded", function () {
    // click the bell to set list as hidden initially
    click_bell();
    // we update the notifications on reload
    update_notifications();
});

window.addEventListener('click', function (e) {
    /**
     * event listener for a mouse click
     * we toggle the notifications with a click on the bell
     * if the notifications are open, a click anywhere else will close them
     */
    let menus = document.getElementsByClassName(notify_menu_class)

    if (document.getElementById('busybell').contains(e.target)) {
        click_bell();
    } else {
        let pressedbell = false;
        for (var i = 0; i < menus.length; i++) {
            if (!menus[i].contains(e.target) && menus[i].classList.contains("visible-list")) {
                pressedbell = true;
            }
        }
        if (pressedbell)
            click_bell();
    }
});

function my_fill_notification_badge(data) {
    var badges = document.getElementsByClassName(notify_badge_class);
    if (badges) {

        for (var i = 0; i < badges.length; i++) {
            if (data.unread_count > 0)
                badges[i].innerHTML = `<span class="dot"><p>${data.unread_count}</p></span>`;
            else
                badges[i].innerHTML = `<span></span>`;
        }
    }
}

function parse_invitation_list(data) {
    // parses the list of notification into a HTML list
    var menus = document.getElementsByClassName(notify_menu_class);
    if (menus) {
        var messages = data.unread_list.map(function (item) {
            message = ""
            switch (item.verb) {
                case "event invite":
                    message += `${item.actor} has <span style="color:green;">invited</span> you to join an event:</br><i>${item.data.title}</i></br>`
                    message += `<button id="id_notif_invite_accept" type="button" onclick="invitation_respond('event', 'accept', ${item.data.invite_id}, ${item.id}); return false;">✓</button>`
                    message += `<button id="id_notif_invite_reject" type="button" onclick="invitation_respond('event', 'reject', ${item.data.invite_id}, ${item.id}); return false;">✗</button>`
                    break;
                case "event invite accepted":
                    message += `${item.actor} has <span style="color:green;">accepted</span> your invite for the event:</br>${item.data.title}`
                    break;
                case "event invite rejected":
                    message += `${item.actor} has <span style="color:red;">declined</span> your invite for the event:</br>${item.data.title}`
                    break;
                case "participant deleted":
                    message += `${item.actor} has <span style="color:red;">removed</span> you from the event:</br>${item.data.title}`
                    break;
                case "participant left":
                    message += `${item.actor} has <span style="color:red;">left</span> your event:</br>${item.data.title}`
                    break;
                case "invite deleted":
                    message += `${item.actor} has <span style="color:red;">removed</span> you from the event:</br>${item.data.title}`
                    break;
                case "event deleted":
                    message += `${item.actor} has <span style="color:red;">deleted</span> the event:</br>${item.data.title}`
                    break;
                case "event edited":
                    message +=`${item.actor} has <span style="color:blue;">edited</span> the event:</br>${item.data.title}`
                    break;
                case "time selected":
                    message += `${item.actor} has <span style="color:green;"> picked a time </span> for the event:</br>${item.data.title}`
                    break;
                case "friend request":
                    message += `${item.actor} has <span style="color:green;">sent</span> you a friend request</br>`
                    message += `<button id="id_notif_invite_accept" type="button" onclick="invitation_respond('friend', 'accept', ${item.data.request_id}, ${item.id});">✓</button>`
                    message += `<button id="id_notif_invite_reject" type="button" onclick="invitation_respond('friend', 'reject', ${item.data.request_id}, ${item.id});">✗</button>`
                    break;
                case "friend request accepted":
                    message += `${item.actor} has <span style="color:green;">accepted</span> your friend request</br>`
                    break;
                case "friend request rejected":
                    message += `${item.actor} has <span style="color:green;">declined</span> your friend request</br>`
                    break;

                default:
                    break;
            }
            refresh = window.location.href.endsWith(item.data.url) || item.data.url === "" ? "return false" : "return true";
            return `<a href="${item.data.url}" onclick="mark_notification(${item.id});${refresh}"><li>${message}</li></a>`
        }).join('')

        for (var i = 0; i < menus.length; i++) {
            if (data.unread_count > 0) {
                menus[i].innerHTML = messages;
            }
            else {
                menus[i].innerHTML = "You have no notifications";
                menus[i].classList.add("nothing-text")
    
            }
        }
    }
}

function update_notifications() {
    return $.ajax({
        url: "/inbox/notifications/api/unread_list/?max=5",
        type: "GET",
        async: true,
    }).done((r) => {
        parse_invitation_list(r);
        my_fill_notification_badge(r);
        return 0;
    }).fail((request, errtxt, errstatus) => {
        return 0;
    });
}

function mark_notification(notif_id) {
    return $.ajax({
        url: "/mark_notification_as_read/" + notif_id + "/",
        type: "POST",
        headers: {
            "X-CSRFToken": csrftoken
        },
        async: true
    }).done(() => {
        update_notifications();
    }).fail(() => {
        alert("fail")
    });
}

function invitation_respond(type, answer, invite_id, notif_id) {

    invite_req = () => $.ajax({
        url: "/" + type + "_invite_" + answer + "/" + invite_id + "/",
        type: "POST",
        headers: {
            "X-CSRFToken": csrftoken
        },
        async: true
    }).fail((request, errtxt, errstatus)=>{
        console.log(request, errtxt, errstatus)
    });

    return $.when(mark_notification(notif_id), invite_req()).done(() => {
        update_notifications();
        if (window.location.href.endsWith("/mypage/")) {
            window.location.reload();
        }
    });
}

