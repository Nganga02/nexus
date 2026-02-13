from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
)

from django.http import HttpResponse

from django.contrib.auth import get_user_model

from .service import MpesaService, MpesaClient

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

from .tasks import process_mpesa_callback

from .permissions import (
    UsersPermission,
    PropertyPermissions,
    BookingPermissions,
    IsGuestForPayment,
)

CustomUser = get_user_model()


# ===========================
# USERS
# ===========================

@extend_schema_view(
    list=extend_schema(summary="List users"),
    retrieve=extend_schema(summary="Retrieve user details"),
    create=extend_schema(
        summary="Create user",
        request=CustomUserCreateSerializer,
        responses={201: CustomUserDetailSerializer},
    ),
    update=extend_schema(summary="Update user"),
    partial_update=extend_schema(summary="Partially update user"),
    destroy=extend_schema(summary="Delete user"),
)
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
    

# ===========================
# PROPERTIES
# ===========================

@extend_schema_view(
    list=extend_schema(summary="List properties"),
    retrieve=extend_schema(summary="Retrieve property details"),
    create=extend_schema(
        summary="Create property",
        request=PropertyDetailSerializer,
        responses={201: PropertyDetailSerializer},
    ),
    update=extend_schema(summary="Update property"),
    destroy=extend_schema(summary="Delete property"),
)
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


# ===========================
# BOOKINGS
# ===========================

@extend_schema_view(
    list=extend_schema(summary="List bookings"),
    retrieve=extend_schema(summary="Retrieve booking details"),
    create=extend_schema(
        summary="Create booking",
        request=BookingDetailSerializer,
        responses={201: BookingDetailSerializer},
    ),
    update=extend_schema(summary="Update booking"),
    destroy=extend_schema(summary="Cancel booking"),
)
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
    


# ===========================
# PAYMENTS
# ===========================

@extend_schema_view(
    list=extend_schema(summary="List payments"),
    retrieve=extend_schema(summary="Retrieve payment details"),
)
class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] #IsGuestForPayment]
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
    
    @extend_schema(
        summary="Create payment and initiate Mpesa STK push",
        description=(
            "Creates a payment record and initiates an Mpesa STK push. "
            "Mpesa callback will later confirm or fail the payment."
        ),
        request=PaymentCreateSerializer,
        responses={
            201: PaymentDetailSerializer,
            400: OpenApiResponse(description="Invalid request"),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            payment = serializer.save()

            # Initiate Mpesa STK push
            mpesa_service = MpesaService(
                phone_number=payment.payer.phone_number,
                amount=payment.amount,
                reference=str(payment.id),
            )

            mpesa_response = mpesa_service.initiate_stk_push()

            checkout_id = mpesa_response.get("CheckoutRequestID")

            if not checkout_id:
                raise Exception("Mpesa did not return checkout ID")
            
            payment.checkout_request_id = checkout_id
            payment.save()

        return Response(
            {
                "payment_id": payment.id,
                "message": "STK push sent to phone",
                "mpesa_response": mpesa_response,
            },
            status=status.HTTP_201_CREATED,
        )
    

@method_decorator(csrf_exempt, name="dispatch")
class MpesaCallbackView(APIView):
    permission_classes = [AllowAny]


    @extend_schema(
        summary="Mpesa STK callback endpoint",
        description="Safaricom Mpesa callback URL for payment confirmation",
        request=dict,
        responses={
            200: OpenApiResponse(description="Callback processed successfully"),
        },
        auth=None,
    )
    def post(self, request):
        print("=== MPESA CALLBACK RECEIVED ===")
        data = request.data

        response = process_mpesa_callback(data)# Allows handling of mpesa callbacks

        # result_code = data["Body"]["stkCallback"]["ResultCode"]
        # checkout_id = data["Body"]["stkCallback"]["CheckoutRequestID"]

        # payment = Payment.objects.filter(
        #     checkout_request_id=checkout_id
        # ).first()

        # if not payment:
        #     return Response({"ResultCode": 0})

        # if result_code == 0:
        #     payment.status = Payment.Status.SUCCESSFUL
        #     ref=self._extract_receipt(data)
        #     print(f"****************************{ref}\n\n")
        #     payment.mpesa_ref = ref
        # else:
        #     payment.status = Payment.Status.FAILED

        # payment.save(update_fields=["status", "mpesa_ref"])

        return Response(response)


