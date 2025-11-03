from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('news.urls_api')),  # all API URLs will now be under /api/
]
