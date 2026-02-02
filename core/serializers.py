from serializers import ModelSerializer
from models import (
    CustomUser,
    Property,
    Booking,
    Payment,
)

"""
Creating serializers for different methods of data representation for the 
models defined in core/models.py
"""

class CustomUserListSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'role']


"""
Used when fetching a single user's detailed information
"""
class CustomUserDetailSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'name',
            'id_photo',
            'email',
            'phone_number',
            'role',
            'credit_score',
            'date_joined',
        ]


class CustomUserSummarySerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'role']

"""
Used when fetching a list of properties with limited details
"""
class PropertyListSerializer(ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'name',
            'description',
            'location',
            'price_per_night',
        ]

"""
Used when fetching detailed information about a single property
"""
class PropertyDetailSerializer(ModelSerializer):
    owner = CustomUserSummarySerializer(read_only=True)
    class Meta:
        model = Property
        fields = [
            'id',
            'owner',
            'name',
            'description',
            'location',
            'amenities',
            'price_per_night',
            'created_at',
        ]


"""
Used when fetching a summary of a property
"""
class PropertySummarySerializer(ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'id',
            'name',
            'location',
            'price_per_night'
        ]


class BookingListSerializer(ModelSerializer):
    property = PropertySummarySerializer(read_only=True)
    class Meta:
        model = Booking
        fields = [
            'id',
            'property',
            'check_in',
            'check_out',
            'status',
        ]

class BookingDetailSerializer(ModelSerializer):
    guests = CustomUserSummarySerializer(many=True, read_only=True)
    property = PropertySummarySerializer(read_only=True)
    class Meta:
        model = Booking
        fields = [
            'id',
            'property',
            'guests',
            'check_in',
            'check_out',
            'price_per_night',
            'total_price',
            'status',
            'created_at',
        ]

class BookingSummarySerializer(ModelSerializer):
    property = PropertySummarySerializer(read_only=True)
    class Meta:
        model = Booking
        fields = [
            'id',
            'property',
            'check_in',
            'check_out',
            'status',
        ]

class PaymentDetailSerializer(ModelSerializer):
    booking = BookingSummarySerializer(read_only=True)
    payer = CustomUserSummarySerializer(read_only=True)
    class Meta:
        model = Payment
        fields = [
            'id',
            'payer',
            'booking',
            'amount',
            'payment_method',
            'payment_date',
        ]