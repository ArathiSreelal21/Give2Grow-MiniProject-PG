from django.db import models
from django.contrib.auth.models import User

class Donation(models.Model):
    CAUSE_CHOICES = [
        ('Education', 'Education Support'),
        ('Food', 'Food Donation'),
        ('Healthcare', 'Healthcare Assistance'),
        ('Shelter', 'Shelter Provision'),
    ]
    
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Picked', 'Picked Up'),
        ('Approved', 'Approved'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    cause = models.CharField(max_length=50, choices=CAUSE_CHOICES)
    food_type = models.CharField(max_length=255, blank=True, null=True)  # Optional for non-food donations
    food_quantity = models.CharField(max_length=100, blank=True, null=True)  # Optional for non-food donations
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Available')  # Added field to track status
    approved_volunteer = models.ForeignKey(
        'UserRegistration', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        limit_choices_to={'user_type': 'Volunteer', 'is_approved': True}
    )

    def __str__(self):
        return f"{self.name} - {self.cause}"


# Model for orphanages
class Orphanage(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    contact = models.CharField(max_length=15)
    amount_needed = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


# Model for educational institutions
class EducationalInstitution(models.Model):
    name = models.CharField(max_length=100)
    institution_type = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    amount_needed = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


# Model for user registration
# Model for user registration
class UserRegistration(models.Model):
    USER_TYPE_CHOICES = [
        ('user', 'user'),
        ('Volunteer', 'Volunteer'),
        ('Organization', 'Organization'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES)
    password = models.CharField(max_length=255)  # Store hashed passwords
    is_approved = models.BooleanField(default=False)  # Whether the volunteer is approved
    notification = models.TextField(blank=True, null=True)  # Notification field

    def __str__(self):
        return self.full_name

from django.utils import timezone

class PaymentHistory(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )

    name = models.CharField(max_length=255)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    otp = models.CharField(max_length=6)  # Assuming 6 digits OTP
    card_last_four = models.CharField(max_length=4, blank=True, null=True)  # Last 4 digits of the card
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.amount} - {self.status}"




class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_requested = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    date_requested = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_requested} requested by {self.user.username}"