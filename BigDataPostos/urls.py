from django.contrib import admin
from django.urls import path, include

urlpatterns = [
     path('admin/', admin.site.urls),
     path('' , include('postos_app.urls')),
     path('' , include('dash_postos.urls'))
]
