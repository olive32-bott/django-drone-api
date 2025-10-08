from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import RedirectView  # <-- add this

urlpatterns = [
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),  # <-- root -> docs
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include(('fleet.urls', 'fleet'), namespace='fleet')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
