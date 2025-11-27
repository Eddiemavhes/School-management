from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class AdministratorManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class Administrator(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'"
            )
        ]
    )
    failed_login_attempts = models.PositiveIntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = AdministratorManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Administrator'
        verbose_name_plural = 'Administrators'

class AcademicYear(models.Model):
    year = models.CharField(max_length=4)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Academic Year {self.year}"

    class Meta:
        ordering = ['-year']

class Term(models.Model):
    name = models.CharField(max_length=50)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    start_date = models.DateField()
    end_date = models.DateField()
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.academic_year}"

    class Meta:
        ordering = ['start_date']

class Teacher(models.Model):
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.surname}"

    class Meta:
        ordering = ['surname', 'first_name']

class Class(models.Model):
    GRADE_CHOICES = [(i, f"Grade {i}") for i in range(1, 8)]
    SECTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
    ]

    grade_level = models.IntegerField(
        choices=GRADE_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    section = models.CharField(max_length=1, choices=SECTION_CHOICES)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='classes')
    teacher = models.OneToOneField(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_class'
    )

    def __str__(self):
        return f"Grade {self.grade_level}{self.section}"

    class Meta:
        verbose_name_plural = "Classes"
        ordering = ['grade_level', 'section']
        unique_together = ['grade_level', 'section', 'academic_year']

class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    birth_entry_number = models.CharField(max_length=50, unique=True)
    current_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.surname}, {self.first_name}"

    class Meta:
        ordering = ['surname', 'first_name']

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('MOBILE', 'Mobile Money'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    receipt_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Payment {self.receipt_number} - {self.student}"

    class Meta:
        ordering = ['-payment_date']
