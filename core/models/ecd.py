from django.db import models
from django.utils import timezone
from decimal import Decimal


class ECDClassProfile(models.Model):
    """Extra configuration for ECD classes (A/B) providing premium features."""
    cls = models.OneToOneField('Class', on_delete=models.CASCADE, related_name='ecd_profile')
    capacity = models.PositiveIntegerField(default=30, help_text="Maximum pupils in this ECD class")
    premium = models.BooleanField(default=False, help_text="Marks this ECD class as a premium offering")
    meal_plan_fee = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    nappies_fee = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    materials_fee = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ECD Profile: {self.cls}"


class ECDClassFee(models.Model):
    """Per-term / per-class additional fees for ECD classes (applied on top of TermFee)."""
    cls = models.ForeignKey('Class', on_delete=models.CASCADE, related_name='ecd_fees')
    term = models.ForeignKey('AcademicTerm', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cls', 'term']

    def __str__(self):
        return f"{self.cls} - {self.term} : {self.amount}"
