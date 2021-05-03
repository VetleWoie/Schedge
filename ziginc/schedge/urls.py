from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from .views import signUpView, friend_request_answer, friend_request_send
import notifications.urls
from django.conf.urls import url


urlpatterns = [
    path("mypage/", views.mypage, name="mypage"),
    path("createevent/", views.create_event, name="createevent"),
    path("event/<int:event_id>/", views.event, name="event"),
    path(
        "event/<int:event_id>/delete/<int:timeslot_id>/",
        views.timeslot_delete,
        name="timeslot_delete",
    ),
    path("event/<int:event_id>/select/", views.timeslot_select, name="timeslot_select"),
    path("event/<int:event_id>/edit/", views.eventedit, name="eventedit"),
    path("event/<int:event_id>/edit/delete/", views.event_delete, name="event_delete"),
    path("event/<int:event_id>/invite/", views.event_invite, name="event_invite"),
    path("event/<int:event_id>/participant_delete/<int:user_id>/", views.participant_delete, name="participant_delete"),
    path("event/<int:event_id>/participant_leave/<int:user_id>/", views.participant_leave, name="participant_leave"),
    path("event_invite_accept/<int:invite_id>/", views.invite_accept, name="invite_accept"),
    path("event_invite_reject/<int:invite_id>/", views.invite_reject, name="invite_reject"),
    path("invite_delete/<int:invite_id>/", views.invite_delete, name="invite_delete"),
    path("signup/", signUpView, name="signup"),
    path("", views.home, name="home"),
    path("", include("django.contrib.auth.urls")),
    path(
        "mark_notification_as_read/<int:notif_id>/",
        views.mark_notification_as_read,
        name="mark_notif_as_read",
    ),
    url("^inbox/notifications/", include(notifications.urls, namespace="notifications")),
    path("signup/termsandservices/", views.termsandservices, name="tands"),
    path("mypage/delete_user_account/", views.delete_user, name="delete_user_account"),

    path("friend_request_invite_accept/<int:invite_id>/", friend_request_answer, name='friend_request_answer'),
    path("friend_request_send/", friend_request_send, name='friend_request_send'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
