const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

function my_fill_notification_badge(data) {
    var badges = document.getElementsByClassName(notify_badge_class);
    if (badges) {

        for (var i = 0; i < badges.length; i++) {
            if (data.unread_count > 0)
                badges[i].innerHTML = "<span class=\"dot\"><p>" + data.unread_count + "</p></span>";
            else
                badges[i].innerHTML = "";
        }
    }
}

function parse_invitation_list(data) {
    // parses the list of notification into a HTML list
    var menus = document.getElementsByClassName(notify_menu_class);
    if (menus) {
        var messages = data.unread_list.map(function (item) {
            message = ""
            if (item.verb === "invite") {
                message += item.actor + " has invited you to join an event:</br><i>" + item.data.title + "</i></br>"
                message += "<button type=\"button\" onclick=\"invitation_respond('accept', " + item.data.invite_id + ", " + item.id + ")\">✓</button>"
                message += "<button type=\"button\" onclick=\"invitation_respond('reject', " + item.data.invite_id + ", " + item.id + ")\">✗</button>"
                // TODO: add buttons for accept and reject
            }
            if (item.verb === "invite accept") {
                message += item.actor + " has <span style=\"color:green;\">accepted</span> your invite for the event:</br>" + item.data.title
            }
            if (item.verb === "invite reject") {
                message += item.actor + " has <span style=\"color:red;\">declined</span> your invite for the event:</br>" + item.data.title
            }
            eventid = item.data.url
            url = "/mark_notification_as_read/" + item.id + "/"
            return '<span style="cursor:pointer;" onclick="mark_notification(' + item.id + ')"><li>' + message + '</li></span>';
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

function update_notificaions() {
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
        update_notificaions();
    });
}

function invitation_respond(type, invite_id, notif_id) {
    invite_req = () => $.ajax({
        url: "/invite_" + type + "/" + invite_id + "/",
        type: "POST",
        headers: {
            "X-CSRFToken": csrftoken
        },
        async: true
    });

    $.when(mark_notification(notif_id), invite_req()).done(() => {
        update_notificaions();
        if (window.location.href.endsWith("/mypage/")) {
            window.location.reload();
        }
    });
}

// we update the notifications on reload
update_notificaions();