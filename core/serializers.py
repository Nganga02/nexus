"""
Handles the validation and transformation of the data for the models
defined in core/models.py, ensuring that the data is in the correct
format and adheres to the business rules before it is saved to the 
database or sent in API responses.
"""



from serializers import ModelSerializer
import serializers
from serializers import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DValidationError
from django.db import transaction, IntegrityError
from datetime import date
from models import (
    Property,
    Booking,
    Payment,
)


"""Dynamically get the CustomUser model"""
CustomUser = get_user_model()


"""
Creating serializers for different methods of data representation for the 
models defined in core/models.py
"""
class CustomUserListSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'role']


"""
Used when fetching a single user's detailed information
"""
class CustomUserDetailSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'name',
            'phone_number',
            'role',
            'date_joined'
        ]

    
    

class CustomUserCreateSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'name',
            'phone_number',
            'role',
            'password',
            'id_photo'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate_password(self, password):
        try:
            validate_password(password)
        except DValidationError as e:
            raise ValidationError(e.messages)
        return password
    
    
    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        try:
            user = CustomUser.objects.create(**validated_data)
            user.set_password(password)
            user.save()
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                raise ValidationError("A user with this email or phone number already exists.")
            else:
                raise ValidationError("An error occurred while creating the user.")
        return user


class CustomUserUpdateSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'email',
            'name',
            'phone_number',
            'role',
            'password',
            'id_photo'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate_password(self, password):
        try:
            validate_password(password)
        except DValidationError as e:
            raise ValidationError(e.messages)
        return password
    
    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.full_clean()
            instance.save()
            if password:
                instance.set_password(password)
                instance.save(update_fields=['password'])
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                raise ValidationError("A user with this email or phone number already exists.")
            else:
                raise ValidationError("An error occurred while updating the user.")
        return instance


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


"""
Used when fetching a list of bookings, includes nested details about the property"""
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


"""
Used when fetching detailed information about a single booking, includes nested details about the property and guests"""
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


"""
Used for creating new bookings, includes validation to ensure booking dates are valid and property is available
"""  
class BookingCreateSerializer(ModelSerializer):
    guests = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CustomUser.objects.all()
    )
    class Meta:
        model = Booking
        fields = [
            'property',
            'guests',
            'check_in',
            'check_out',
            'price_per_night',
        ]

    def validate(self, data):
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        property = data.get('property')


        if check_in >= check_out:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date."
            )
        
        if check_in < date.today():
            raise serializers.ValidationError(
                "Check-in date cannot be in the past."
            )
        
        if property and not property.is_available(check_in, check_out):
            raise serializers.ValidationError(
                "Property is not available for the selected dates."
            )

        return data
    
    @transaction.atomic
    def create(self, validated_data):
        guests=validated_data.pop('guests')

        booking = Booking.objects.create(**validated_data)
        booking.guests.set(guests)
        nights = booking.get_number_of_nights()
        booking.total_price = nights * booking.price_per_night
        booking.save(update_fields=['total_price'])
        return booking
    


# Used for updating existing bookings 
class BookingUpdateSerializer(ModelSerializer):
    guests = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CustomUser.objects.all()
    )
    class Meta:
        model = Booking
        fields = [
            'property',
            'guests',
            'check_in',
            'check_out',
            'price_per_night',
        ]
    
    def validate(self, data):
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        property = data.get('property')


        if check_in >= check_out:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date."
            )
        
        if check_in < date.today():
            raise serializers.ValidationError(
                "Check-in date cannot be in the past."
            )
        
        if property and not property.is_available(check_in, check_out):
            raise serializers.ValidationError(
                "Property is not available for the selected dates."
            )

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        guests = validated_data.pop('guests', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.full_clean()
        instance.save()

        if guests is not None:
            instance.guests.set(guests)

        if(any(field in validated_data for field in [
            'check_in', 'check_out', 'price_per_night'])):
            nights = (instance.check_out - instance.check_in).days
            instance.total_price = instance.calculate_total_price(nights)
            instance.save(update_fields=['total_price'])

        return instance
    


"""
Used for fetching a summary of a booking, typically when included in payment details"""
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



"""
Used for fetching a detailed information information about a payment
"""
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
            'payment_date',
            'payment_method',
            'status',
        ]


"""
Used for creating a new payment, includes validation to ensure payment amount is valid and payer is a guest of the booking
We only allow creating payments ans not updating to maintain payment integrity
"""
class PaymentCreateSerializer(ModelSerializer):
    booking = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.filter(status='processing')
    )
    payer = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Payment
        fields = [
            'payer',
            'booking',
            'amount',
            'payment_method',
        ]

    def validate(self, data):
        booking = data.get('booking')
        amount = data.get('amount')
        payer = data.get('payer')

        if payer is None or not booking.guests.filter(id=payer.id).exists():
            raise serializers.ValidationError(
                "Payer is required and must be a guest of the booking."
            )
        
        if amount <= 0:
            raise serializers.ValidationError(
                "Payment amount must be greater than zero."
            )
        
        #preventing overpayment
        if amount > booking.balance_due:
            raise serializers.ValidationError(
                "Payment amount cannot exceed the balance due."
            )

        return data
    
    @transaction.atomic
    def create(self, validated_data):
        booking = (
            Booking.objects
            .select_for_update()
            .get(id=validated_data['booking'].id)
        )
        payment = Payment.objects.create(**validated_data)
        booking = payment.booking
        booking.balance_due = booking.calculate_balance_due(payment.amount)
        booking.save(update_fields=['balance_due', 'status'])
        return payment
