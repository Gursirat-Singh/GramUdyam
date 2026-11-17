from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


LANGUAGE_CHOICES = [
    ("en", "English"),
    ("hi", "Hindi (हिन्दी)"),
    ("pa", "Punjabi (ਪੰਜਾਬੀ)"),
    ("mr", "Marathi (मराठी)"),
    ("ta", "Tamil (தமிழ்)"),
    ("te", "Telugu (తెలుగు)"),
    ("bn", "Bengali (বাংলা)"),
]

INDIAN_STATE_CHOICES = [
    ("Punjab", "Punjab"),
    ("Haryana", "Haryana"),
    ("Uttar Pradesh", "Uttar Pradesh"),
    ("Rajasthan", "Rajasthan"),
    ("Madhya Pradesh", "Madhya Pradesh"),
    ("Bihar", "Bihar"),
    ("Maharashtra", "Maharashtra"),
    ("Gujarat", "Gujarat"),
    ("Karnataka", "Karnataka"),
    ("Tamil Nadu", "Tamil Nadu"),
    ("Telangana", "Telangana"),
    ("Andhra Pradesh", "Andhra Pradesh"),
    ("West Bengal", "West Bengal"),
    ("Odisha", "Odisha"),
    ("Assam", "Assam"),
    ("Himachal Pradesh", "Himachal Pradesh"),
    ("Uttarakhand", "Uttarakhand"),
    ("Chhattisgarh", "Chhattisgarh"),
    ("Jharkhand", "Jharkhand"),
    ("Kerala", "Kerala"),
    ("Other", "Other State / UT"),
]


class UserProfile(models.Model):
    """Stores hyper-local rural entrepreneur profile, skills, language, and capital."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    state = models.CharField(
        max_length=100,
        choices=INDIAN_STATE_CHOICES,
        default="Punjab",
        help_text="State or Union Territory where your enterprise operates.",
    )
    district = models.CharField(
        max_length=100,
        default="",
        blank=True,
        help_text="District name (e.g., Ludhiana, Karnal, Nashik).",
    )
    village_or_town = models.CharField(
        max_length=150,
        default="",
        blank=True,
        help_text="Village, Gram Panchayat, Block, or semi-urban town.",
    )
    preferred_language = models.CharField(
        max_length=30,
        choices=LANGUAGE_CHOICES,
        default="en",
        help_text="Preferred language for advisory explanations.",
    )
    business_interests = models.TextField(
        blank=True,
        default="",
        help_text="Sectors of interest (e.g., dairy processing, millet snacks, solar irrigation, custom hiring).",
    )
    skills = models.TextField(
        blank=True,
        default="",
        help_text="Existing vocational, agricultural, craft, or business skills.",
    )
    available_capital = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("50000.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Own savings / equity capital available to invest (in INR ₹).",
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Contact number for SHG / bank coordination (optional).",
    )
    experience_years = models.PositiveIntegerField(
        default=0,
        help_text="Years of prior farming, trade, or micro-enterprise experience.",
    )
    shg_or_fpo_member = models.BooleanField(
        default=False,
        help_text="Are you a member of a Self-Help Group (SHG) or Farmer Producer Organization (FPO)?",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["state", "district"], name="idx_profile_location"),
        ]
        verbose_name = "Entrepreneur Profile"
        verbose_name_plural = "Entrepreneur Profiles"

    def __str__(self):
        loc = f"{self.village_or_town}, {self.district}" if self.village_or_town else self.state
        return f"{self.user.username} ({loc})"
