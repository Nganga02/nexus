from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import (
    UserViewSet,
    PropertyViewSet,
    BookingViewSet,
    PaymentViewSet,
)

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='user')
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    # path('pay/', index, name='pay'),
]
