from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# from wgt_backend.scheduler import start_scheduler

urlpatterns = [
    # Django Stuff
    path('admin/', admin.site.urls),

    # Project Apps
    path('schedule/', include('apps.schedule.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# start_scheduler()
