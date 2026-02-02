import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from .managers import CustomUserManager

User = get_user_model()

ADMIN = "admin"
GUEST = "guest"
HOST = "host"
PENDING = "pending"
CONFIRMED = "confirmed"
CANCELLED = "cancelled"

class CustomUser(AbstractBaseUser, PermissionsMixin):
    #Required fields
    id = models.CharField(primary_key=True, editable=False)
    name = models.CharField(max_length=150)
    id_photo = models.ImageField(upload_to="users/photos/", blank=False, null=False)
    phone_number = models.CharField(max_length=20, unique=True, blank=False, null=False)
    password = models.CharField(max_length=128)

    #Optional fields
    email = models.EmailField(blank=True, null=True)
    credit_score = models.IntegerField(default=0)
    ROLE_CHOICES = (
        (ADMIN, "Admin"),
        (GUEST, "Guest"),
        (HOST, "Host"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=GUEST)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()

    USERNAME_FIELD = "id"
    REQUIRED_FIELDS = ['id', 'id_photo', 'phone_number', 'name', 'password']

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

    def __str__(self):
        return f"{self.title} - {self.address}"
    


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name="bookings"
    )
    guest = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="bookings"
    )

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (CANCELLED, 'Canceled'),
    ]
    check_in = models.DateField()
    check_out = models.DateField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Validate booking dates and availability"""
        from django.core.exceptions import ValidationError
        
        # Validate end_date is after start_date
        if self.end_date <= self.start_date:
            raise ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        # Validate dates are not in the past
        if self.start_date < timezone.now().date():
            raise ValidationError({
                'start_date': 'Start date cannot be in the past.'
            })
        
        # Check property availability (exclude current booking if updating)
        if not self.property.is_available(self.start_date, self.end_date):
            if self._state.adding or not Booking.objects.filter(
                booking_id=self.booking_id,
                start_date=self.start_date,
                end_date=self.end_date
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
        return (self.end_date - self.start_date).days
    
    def can_cancel(self):
        """Check if booking can be canceled"""
        return self.status in ['pending', 'confirmed'] and self.start_date > timezone.now()


    def calculate_total_price(self):
        delta = self.check_out - self.check_in
        self.total_price = delta.days * self.property.price_per_night
        self.save()

    def __str__(self):
        return f"Booking {self.id} price: {self.total_price} status: {self.status}"