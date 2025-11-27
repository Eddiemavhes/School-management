from django.db import models
from django.utils import timezone

class SchoolDetails(models.Model):
    """Store school information displayed in header and system"""
    
    school_name = models.CharField(max_length=255, unique=True, default="Your School Name")
    school_motto = models.CharField(max_length=500, blank=True, default="Quality Education for All")
    school_code = models.CharField(max_length=50, unique=True, blank=True, default="SCH001")
    
    # Contact Information
    principal_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    alternate_phone = models.CharField(max_length=20, blank=True)
    
    # Address
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # School Details
    established_year = models.IntegerField(blank=True, null=True)
    school_type = models.CharField(
        max_length=50,
        choices=[
            ('PRIMARY', 'Primary School'),
            ('SECONDARY', 'Secondary School'),
            ('HIGHER_SECONDARY', 'Higher Secondary School'),
            ('COMBINED', 'Combined School'),
        ],
        default='COMBINED'
    )
    board_affiliation = models.CharField(max_length=200, blank=True)
    
    # Logo and Colors
    logo_url = models.URLField(blank=True)
    header_color = models.CharField(max_length=7, default="#1e40af", help_text="Header background color (hex)")
    accent_color = models.CharField(max_length=7, default="#0891b2", help_text="Accent color (hex)")
    
    # Registration
    registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    
    # Working Days
    working_days_per_week = models.IntegerField(default=6, choices=[(5, "5 Days"), (6, "6 Days")])
    
    # Fees Configuration
    enable_online_payments = models.BooleanField(default=False)
    payment_gateway = models.CharField(
        max_length=50,
        choices=[
            ('NONE', 'None'),
            ('STRIPE', 'Stripe'),
            ('RAZORPAY', 'Razorpay'),
            ('PAYPAL', 'PayPal'),
        ],
        default='NONE'
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "School Details"
        verbose_name_plural = "School Details"
    
    def __str__(self):
        return self.school_name
    
    def get_full_address(self):
        """Return formatted full address"""
        parts = [self.street_address, self.city, self.state, self.postal_code, self.country]
        return ", ".join(filter(None, parts))

    @classmethod
    def get_or_create_default(cls):
        """Get existing or create default school details"""
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'school_name': 'Your School Name',
                'school_motto': 'Quality Education for All',
                'school_code': 'SCH001',
                'principal_name': '',
                'email': 'school@example.com',
                'phone': '+1-XXX-XXX-XXXX',
            }
        )
        return obj
