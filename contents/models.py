from django.db import models
from django.contrib.auth.models import User

class Donor(models.Model):
    donorID = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    donorIC = models.CharField(max_length=20)
    donorName = models.CharField(max_length=100)
    contactNumber = models.CharField(max_length=20)
    emailAddress = models.EmailField()


class DonationCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name


class Donation(models.Model):
    DONATION_TYPES = [
        ('General', 'General'),
        ('Mosque Maintenance', 'Mosque Maintenance'),
        ('Charity', 'Charity'),
    ]

    PAYMENT_METHODS = [
        ('Credit/Debit Card', 'Credit/Debit Card'),
        ('Online Banking', 'Online Banking'),
        ('QR Code', 'QR Code'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    donation_type = models.ForeignKey(DonationCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    card_number = models.CharField(max_length=20, null=True, blank=True)
    qr_receipt = models.ImageField(upload_to='receipts/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.donorName} - {self.donation_type} - RM{self.amount}"


class AdminProfile(models.Model):
    ROLE_CHOICES = [
        ('Chairman', 'Chairman'),
        ('Treasurer', 'Treasurer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class TreasurerAction(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')])
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

class DonationCategoryRequest(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    treasurer = models.ForeignKey('AdminProfile', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    original_category = models.ForeignKey(DonationCategory, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    data_before = models.TextField(blank=True, null=True)
    data_after = models.TextField(blank=True, null=True)

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
