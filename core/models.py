"""
Models carry the business logic of the applicaiton,
they define the data structure and relationships between different entities.
Has the core implementation of the applications logic and rules on the data
retireved and saved.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        GUEST = "guest", "Guest"
        HOST = "host", "Host"
    #Required fields
    id = models.CharField(primary_key=True, editable=False, unique=True, max_length=100)
    name = models.CharField(max_length=150)
    id_photo = models.ImageField(upload_to="users/photos/", blank=False, null=False)
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        blank=False,
        null=False,
        )
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    #Optional fields
    email = models.EmailField(blank=True, null=True, unique=True)
    credit_score = models.IntegerField(default=0)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.GUEST)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()

    USERNAME_FIELD = "id"
    REQUIRED_FIELDS = ['id_photo', 'phone_number', 'name', 'email', 'password']

    

    def __str__(self):
        return f"{self.name} {self.phone_number}"


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name="properties"
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300)
    amenities = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    #TODO: adding type

    def is_available(self, start_date, end_date):  
        """Check if property is available for the given date range"""
        overlapping_bookings = Booking.objects.filter(
            property=self,
            check_in__lt=end_date,
            check_out__gt=start_date
        )
        return not overlapping_bookings.exists()

    def __str__(self):
        return f"{self.title} - {self.address}"
    


class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELED = 'canceled', 'Canceled'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name="bookings"
    )
    guests = models.ManyToManyField(
        CustomUser, 
        related_name="bookings"
    )

    status = models.CharField(choices=BookingStatus.choices, default=BookingStatus.PENDING)
    check_in = models.DateField()
    check_out = models.DateField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Validate booking dates and availability"""
        from django.core.exceptions import ValidationError
        
        # Validate end_date is after check_in
        if self.check_out <= self.check_in:
            raise ValidationError({
                'check_out': 'Check-out date must be after check-in date.'
            })
        
        # Validate dates are not in the past
        if self.check_in < timezone.now().date():
            raise ValidationError({
                'check_in': 'Check-in date cannot be in the past.'
            })
        
        # Check property availability (exclude current booking if updating)
        if not self.property.is_available(self.check_in, self.check_out):
            if self._state.adding or not Booking.objects.filter(
                check_in=self.check_in,
                check_out=self.check_out
            ).exists():
                raise ValidationError({
                    'property': 'Property is not available for the selected dates.'
                })
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_number_of_nights(self):
        """Get number of nights for this booking"""
        return (self.check_out - self.check_in).days
    
    def can_cancel(self):
        """Check if booking can be canceled"""
        return self.status in ['pending'] and self.check_in > timezone.now().date()

    def calculate_total_price(self):
        delta = self.check_out - self.check_in
        self.total_price = delta.days * self.property.price_per_night
        self.balance_due = self.total_price
    
    def calculate_balance_due(self, amount_paid):
        self.balance_due -= amount_paid
        if self.balance_due > 0:
            self.status = self.BookingStatus.PROCESSING
        else:
            self.status = self.BookingStatus.CONFIRMED
        self.save(update_fields=['status'])
        return self.balance_due

    
    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out__gt=models.F("check_in")),
                name="check_out_after_check_in"
            )
        ]
    
    def __str__(self):
        return f"Booking {self.id} price: {self.total_price} status: {self.status}"


    
class Payment(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "processing", "Processing"
        SUCCESSFUL = "successful", "Successful"
        FAILED = "failed", "Failed"

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    checkout_request_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )
    payer = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name="payments"
    )
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name="payment"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROCESSING,
        db_index=True
    )
    mpesa_ref=models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=100)

    def get_checkout_request_id(self, response):
        self.checkout_request_id = response.get("CheckoutRequestID")

    class Meta:
        indexes=[
            models.Index(fields=['booking', 'payer', 'checkout_request_id'])
        ]

    def __str__(self):
        return f"Payment {self.id} for Booking {self.booking.id} amount: {self.amount}"
    