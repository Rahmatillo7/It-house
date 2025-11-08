from django.urls import path, include
from django.conf.urls.static import static

from config import settings
from .views import LeadUpdateStatusView, TaskCreateView

urlpatterns = [
    path('lead/<int:pk>/update-status/', LeadUpdateStatusView.as_view(), name='lead-update-status'),
    path('task/create/', TaskCreateView.as_view(), name='task-create'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
