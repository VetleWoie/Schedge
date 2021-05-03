const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

function my_fill_notification_badge(data) {
    var badges = document.getElementsByClassName(notify_badge_class);
    if (badges) {

        for (var i = 0; i < badges.length; i++) {
            if (data.unread_count > 0)
                badges[i].innerHTML = "<span class=\"dot\"><p>" + data.unread_count + "</p></span>";
            else
                badges[i].innerHTML = "<span></span>";
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
                case "invite":
                    message += item.actor + " has <span style=\"color:green;\">invited</span> you to join an event:</br><i>" + item.data.title + "</i></br>"
                    message += "<button id=\"id_notif_invite_accept\" type=\"button\" onclick=\"invitation_respond('event', 'accept', " + item.data.invite_id + ", " + item.id + ")\">✓</button>"
                    message += "<button id=\"id_notif_invite_reject\" type=\"button\" onclick=\"invitation_respond('event', 'reject', " + item.data.invite_id + ", " + item.id + ")\">✗</button>"
                    break;
                case "invite accepted":
                    message += item.actor + " has <span style=\"color:green;\">accepted</span> your invite for the event:</br>" + item.data.title
                    break;
                case "invite rejected":
                    message += item.actor + " has <span style=\"color:red;\">declined</span> your invite for the event:</br>" + item.data.title
                    break;
                case "participant deleted":
                    message += item.actor + " has <span style=\"color:red;\">removed</span> you from the event:</br>" + item.data.title
                    break;
                case "participant left":
                        message += item.actor + " has <span style=\"color:red;\">left</span> your event:</br>" + item.data.title
                        break;
                case "invite deleted":
                    message += item.actor + " has <span style=\"color:red;\">removed</span> you from the event:</br>" + item.data.title
                    break;
                case "event deleted":
                    message += item.actor + " has <span style=\"color:red;\">deleted</span> the event:</br>" + item.data.title
                    break;
                case "event edited":
                    message += item.actor + " has <span style=\"color:blue;\">edited</span> the event:</br>" + item.data.title
                    break;
                case "time selected":
                    message += item.actor + " has <span style=\"color:green;\"> picked a time </span> for the event:</br>" + item.data.title

                case "friend request":
                    message += item.actor + " has <span style=\"color:green;\">sent</span> you a friend request</br><i>" + item.data.title + "</i></br>"
                    message += "<button id=\"id_notif_invite_accept\" type=\"button\" onclick=\"invitation_respond('friend_request', 'accept', " + item.data.invite_id + ", " + item.id + ")\">✓</button>"
                    message += "<button id=\"id_notif_invite_reject\" type=\"button\" onclick=\"invitation_respond('friend_request', 'reject', " + item.data.invite_id + ", " + item.id + ")\">✗</button>"
                    break;
                case "friend request accepted":
                    message += item.actor + " has <span style=\"color:green;\">accepted</span> your friend request</br>"
                    break;
                case "friend request rejected":
                    message += item.actor + " has <span style=\"color:green;\">declined</span> your friend request</br>"
                    break;

                default:
                    break;
            }
            return `<a href="${item.data.url}" onclick="mark_notification(${item.id})"><li>${message}</li></a>`
            // return '<span style="cursor:pointer;" onclick="mark_notification(' + item.id + ')"><li>' + message + '</li></span>';
        }).join('')

        for (var i = 0; i < menus.length; i++) {
            if (data.unread_count > 0) {
                menus[i].innerHTML = messages;
                menus[i].classList.remove("invislist")
            }
            else {
                menus[i].innerHTML = "";
                menus[i].classList.add("invislist")
            }
        }
    }
}

function update_notifications() {
    $.ajax({
        url: "/inbox/notifications/api/unread_list/?max=5",
        type: "GET",
        async: true,
    }).done((r) => {
        parse_invitation_list(r);
        my_fill_notification_badge(r);

    });
}

function mark_notification(notif_id) {
    $.ajax({
        url: "/mark_notification_as_read/" + notif_id + "/",
        type: "POST",
        headers: {
            "X-CSRFToken": csrftoken
        },
        async: true
    }).done(() => {
        update_notifications();
    });
}

function invitation_respond(answer, type, invite_id, notif_id) {
    invite_req = () => $.ajax({
        url: "/" + type + "_invite_" + answer + "/" + invite_id + "/",
        type: "POST",
        headers: {
            "X-CSRFToken": csrftoken
        },
        async: true
    });

    $.when(mark_notification(notif_id), invite_req()).done(() => {
        update_notifications();
        if (window.location.href.endsWith("/mypage/")) {
            window.location.reload();
        }
    });
}

// we update the notifications on reload
update_notifications();