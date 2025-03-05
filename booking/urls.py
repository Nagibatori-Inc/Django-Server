from django.urls import path, include

from booking.views import router


urlpatterns = [
    path('', include(router.urls)),
]