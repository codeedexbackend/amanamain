
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from web import views

urlpatterns = [
    path("", views.webpage, name='webpage'),
    path("contact", views.contact, name='contact'),
    path("about", views.about, name='about'),
    path("services", views.services, name='services'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
