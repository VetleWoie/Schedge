from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('createevent/', views.create_event, name='createevent'),
    path('event/<int:event_id>/', views.event, name="event"),
    path('event/<int:event_id>/delete/<int:timeslot_id>/', views.timeslot_delete, name="timeslot_delete"),
    path('event/<int:event_id>/edit/', views.eventedit, name="eventedit"),
    path('event/<int:event_id>/edit/delete/',views.event_delete, name="event_delete" )
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)