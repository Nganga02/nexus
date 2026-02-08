from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Prefetch

from django.contrib.auth import get_user_model

from .models import Property, Booking, Payment
from .serializers import (
    CustomUserListSerializer,
    CustomUserCreateSerializer,
    CustomUserDetailSerializer,
    CustomUserUpdateSerializer,

    PropertyListSerializer,
    PropertyDetailSerializer,

    BookingListSerializer,
    BookingDetailSerializer,

    PaymentCreateSerializer,
    PaymentDetailSerializer,
)

from .permissions import (
    UsersPermission,
    PropertyPermissions,
    BookingPermissions,
    IsGuestForPayment,
)

CustomUser = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [UsersPermission]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return CustomUserUpdateSerializer
        if self.action == 'list':
            return CustomUserListSerializer
        return CustomUserDetailSerializer


class PropertyViewSet(viewsets.ModelViewSet):
    permission_classes = [PropertyPermissions]

    def get_queryset(self):
        return Property.objects.select_related('owner')

    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        return PropertyDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [BookingPermissions]

    def get_queryset(self):
        user = self.request.user

        qs = Booking.objects.select_related(
            'property',
            'property__owner'
        ).prefetch_related('guests')

        if user.role == 'admin':
            return qs

        if user.role == 'host':
            return qs.filter(property__owner=user)

        return qs.filter(guests=user)

    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        return BookingDetailSerializer
    

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsGuestForPayment]

    def get_queryset(self):
        user = self.request.user

        qs = Payment.objects.select_related(
            'booking',
            'payer'
        )

        if user.role == 'admin':
            return qs

        return qs.filter(booking__guests=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentDetailSerializer
