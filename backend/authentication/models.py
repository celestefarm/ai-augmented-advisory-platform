# authentication/models.py
from django.utils import timezone
from django.conf import settings
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator

class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a user with email and password"""
        if not email:
            raise ValueError(_('Email address is required'))
        
        if not password:
            raise ValueError(_('Password is required'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create regular user"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create superuser for admin access"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for AI-Augmented Advisory Platform
    Designed for C-suite professionals making high-stakes decisions
    """
    
    SUBSCRIPTION_TIERS = [
        ('free', _('Free Trial')),
        ('pro', _('Professional')),
        ('enterprise', _('Enterprise')),
    ]

    INDUSTRIES = [
        ('technology', _('Technology')),
        ('finance', _('Finance & Banking')),
        ('healthcare', _('Healthcare & Pharmaceuticals')),
        ('manufacturing', _('Manufacturing')),
        ('retail', _('Retail & E-commerce')),
        ('energy', _('Energy & Utilities')),
        ('telecommunications', _('Telecommunications')),
        ('real_estate', _('Real Estate')),
        ('education', _('Education')),
        ('hospitality', _('Hospitality & Tourism')),
        ('transportation', _('Transportation & Logistics')),
        ('media', _('Media & Entertainment')),
        ('agriculture', _('Agriculture')),
        ('construction', _('Construction')),
        ('consulting', _('Consulting & Professional Services')),
        ('government', _('Government & Public Sector')),
        ('nonprofit', _('Non-Profit')),
        ('other', _('Other')),
    ]

    REGIONS = [
        # Africa
        ('africa_north', _('North Africa')),
        ('africa_west', _('West Africa')),
        ('africa_east', _('East Africa')),
        ('africa_central', _('Central Africa')),
        ('africa_southern', _('Southern Africa')),
        
        # Asia
        ('asia_east', _('East Asia')),
        ('asia_southeast', _('Southeast Asia')),
        ('asia_south', _('South Asia')),
        ('asia_central', _('Central Asia')),
        ('asia_west', _('West Asia/Middle East')),
        
        # Europe
        ('europe_west', _('Western Europe')),
        ('europe_east', _('Eastern Europe')),
        ('europe_north', _('Northern Europe')),
        ('europe_south', _('Southern Europe')),
        
        # Americas
        ('americas_north', _('North America')),
        ('americas_central', _('Central America')),
        ('americas_caribbean', _('Caribbean')),
        ('americas_south', _('South America')),
        
        # Oceania
        ('oceania', _('Oceania')),
    ]

    # Core Identity
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_('Unique user identifier')
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        db_index=True,
        validators=[EmailValidator()],
        help_text=_('Primary authentication credential')
    )
    email_verified = models.BooleanField(
        _('email verified'),
        default=False,
        help_text=_('Designates whether user has verified their email')
    )
    auth_provider = models.CharField(
        max_length=50,
        default='email',
        choices=[
            ('email', 'Email'),
            ('google', 'Google'),
        ],
        help_text=_('Authentication provider used')
    )
    
    # Professional Profile
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=True
    )
    industry = models.CharField(
        _('industry'),
        max_length=100,
        blank=True,
        choices=INDUSTRIES,
        help_text=_('User\'s industry sector')
    )
    region = models.CharField(
        _('region'),
        max_length=50,
        blank=True,
        choices=REGIONS,
        help_text=_('User\'s geographical region')
    )
    role = models.CharField(
        _('role/title'),
        max_length=255,
        blank=True,
        help_text=_('e.g., VP Strategy, CEO, Director')
    )
    
    # Subscription & Access
    subscription_tier = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_TIERS,
        default='free',
        db_index=True,
        help_text=_('User subscription level')
    )
    
    # Account Status
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user account is active')
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can access admin site')
    )
    
    # Activity Tracking
    last_login = models.DateTimeField(
        _('last login'),
        blank=True,
        null=True,
        help_text=_('Last time user logged in')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    # Firebase Integration
    firebase_uid = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        unique=True,
        help_text=_('Firebase user ID for Firestore sync')
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['subscription_tier']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def send_verification_email(self):
        """Send email verification link"""
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from rest_framework_simplejwt.tokens import RefreshToken
        
        token = RefreshToken.for_user(self)
        verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={str(token.access_token)}"
        
        html_message = render_to_string('emails/verify_email.html', {
            'user': self,
            'verification_url': verification_url,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Verify your AI-Augmented account',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
            html_message=html_message,
            fail_silently=False,
        )

    def __str__(self):
        return f"{self.email} ({self.get_full_name() or 'No name'})"

    def get_full_name(self):
        """Return full name or empty string"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else ""

    def get_short_name(self):
        """Return first name or email username"""
        return self.first_name or self.email.split('@')[0]

    @property
    def is_premium(self):
        """Check if user has premium access"""
        return self.subscription_tier in ['pro', 'enterprise']

    @property
    def workspace_limit(self):
        """Get workspace limit based on subscription tier"""
        limits = {
            'free': 3,
            'pro': 20,
            'enterprise': 100,
        }
        return limits.get(self.subscription_tier, 3)

    def to_firestore_dict(self):
        """Convert user data to Firestore-compatible dictionary"""
        return {
            'user_id': str(self.id),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'industry': self.industry,
            'region': self.region,
            'role': self.role,
            'subscription_tier': self.subscription_tier,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }

    def clean(self):
        """Normalize email before saving"""
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)