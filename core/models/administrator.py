from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from .teacher_assignment import TeacherAssignmentHistory

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
        return self.create_user(email, password, **extra_fields)

class Administrator(AbstractBaseUser, PermissionsMixin):
    # Base fields
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)

    # Teacher specific fields
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    teacher_id = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_color = models.CharField(
        max_length=20,
        default='emerald',
        choices=[
            ('emerald', 'Emerald'),
            ('blue', 'Blue'),
            ('purple', 'Purple'),
            ('rose', 'Rose'),
            ('amber', 'Amber'),
        ]
    )

    objects = AdministratorManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Administrator'
        verbose_name_plural = 'Administrators'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def increment_failed_login(self):
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        self.save()
    
    @property
    def initials(self):
        return "".join(name[0].upper() for name in self.full_name.split() if name)
    
    @property
    def current_class(self):
        """Get the teacher's currently assigned class for the active academic year"""
        if not self.is_teacher:
            return None
        
        from .academic_year import AcademicYear
        
        # Get active academic year
        active_year = AcademicYear.objects.filter(is_active=True).first()
        if not active_year:
            return None
        
        # Get the class assigned in the active year
        active_class = self.assigned_class.filter(academic_year=active_year.year).first()
        return active_class if active_class else None

    @property
    def status_color(self):
        if not self.is_teacher:
            return 'gray'
        return 'emerald' if self.is_active else 'rose'

    def assign_to_class(self, class_obj, academic_year):
        if not self.is_teacher:
            raise ValueError("This administrator is not a teacher")
        
        # Check if class is already assigned to another teacher
        if class_obj.teacher and class_obj.teacher != self:
            raise ValueError(f"This class is already assigned to {class_obj.teacher.full_name}")
            
        # End any current active assignments
        current_assignments = TeacherAssignmentHistory.objects.filter(
            teacher=self,
            is_active=True
        )
        for assignment in current_assignments:
            assignment.is_active = False
            assignment.end_date = timezone.now().date()
            assignment.save()
        
        # Create new assignment
        TeacherAssignmentHistory.objects.create(
            teacher=self,
            class_assigned=class_obj,
            academic_year=academic_year,
            start_date=timezone.now().date(),
            is_active=True
        )

    def get_assignment_history(self):
        return self.assignment_history.all().select_related('class_assigned')