from django.contrib import admin
from django.urls import path, include

urlpatterns = [
     path('admin/', admin.site.urls),
<<<<<<< HEAD
     path('' , include('postos_app.urls')),
     path('dashboard/', include('dash_postos.urls'))
=======
     path('' , include('postos_app.urls'))
>>>>>>> 5c8bbf3c846bd4c215f908588cdb6d2f42950ad8
]
