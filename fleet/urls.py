from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import DroneViewSet, MedicationViewSet

app_name = 'fleet'

router = DefaultRouter()
router.register(r'drones', DroneViewSet, basename='drone')
router.register(r'medications', MedicationViewSet, basename='medication')

urlpatterns = [
    path('', include(router.urls)),
]
