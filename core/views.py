from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .models import (
    Property,
    Booking,
    Payment
)

from .serializers import (
    PropertyListSerializer,
    PropertyDetailSerializer,
    BookingListSerializer,
    BookingDetailSerializer,
    CustomUserListSerializer,
    CustomUserDetailSerializer,
    PaymentDetailSerializer,
)

CustomUser = get_user_model()

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()

    def list(self, request, *args, **kwargs):
        self.serializer_class = CustomUserListSerializer
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = CustomUserDetailSerializer
        return super().retrieve(request, *args, **kwargs)   

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()

    def list(self, request, *args, **kwargs):
        self.serializer_class = PropertyListSerializer
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = PropertyDetailSerializer
        return super().retrieve(request, *args, **kwargs)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()

    def list(self, request, *args, **kwargs):
        self.serializer_class = BookingListSerializer
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = BookingDetailSerializer
        return super().retrieve(request, *args, **kwargs)
    
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = PaymentDetailSerializer
        return super().retrieve(request, *args, **kwargs)