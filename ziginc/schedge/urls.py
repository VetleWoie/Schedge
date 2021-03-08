from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from .views import signUpView

urlpatterns = [
    path('mypage/', views.mypage, name='mypage'),
    path('createevent/', views.create_event, name='createevent'),
    path('event/<int:event_id>/', views.event, name="event"),
    path('event/<int:event_id>/delete/<int:timeslot_id>/', views.timeslot_delete, name="timeslot_delete"),
    path('event/<int:event_id>/edit/', views.eventedit, name="eventedit"),
    path('event/<int:event_id>/edit/delete/',views.event_delete, name="event_delete" ),
    path('signup/' ,signUpView,name='signup'),
    path('', TemplateView.as_view(template_name="home.html"), name="home"),
    path('', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
