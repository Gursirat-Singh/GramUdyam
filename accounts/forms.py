from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from accounts.models import UserProfile, INDIAN_STATE_CHOICES, LANGUAGE_CHOICES


class EntrepreneurRegistrationForm(UserCreationForm):
    '''Registration form capturing user credentials and initial rural profile.'''
    first_name = forms.CharField(max_length=150, required=True, label="First Name")
    last_name = forms.CharField(max_length=150, required=False, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    state = forms.ChoiceField(choices=INDIAN_STATE_CHOICES, initial="Punjab", label="State / UT")
    district = forms.CharField(max_length=100, required=True, label="District")
    village_or_town = forms.CharField(max_length=150, required=True, label="Village / Block / Town")
    preferred_language = forms.ChoiceField(choices=LANGUAGE_CHOICES, initial="en", label="Preferred Language")
    available_capital = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.00"),
        initial=Decimal("50000.00"),
        label="Available Startup Capital (₹)",
    )
    skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        label="Existing Skills & Experience",
    )
    business_interests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        label="Business Interests",
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_available_capital(self):
        cap = self.cleaned_data.get("available_capital")
        if cap is not None and cap < Decimal("0.00"):
            raise ValidationError("Available capital cannot be negative.")
        return cap

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.email = self.cleaned_data.get("email", "")
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "state": self.cleaned_data.get("state", "Punjab"),
                    "district": self.cleaned_data.get("district", ""),
                    "village_or_town": self.cleaned_data.get("village_or_town", ""),
                    "preferred_language": self.cleaned_data.get("preferred_language", "en"),
                    "available_capital": self.cleaned_data.get("available_capital") or Decimal("0.00"),
                    "skills": self.cleaned_data.get("skills", ""),
                    "business_interests": self.cleaned_data.get("business_interests", ""),
                },
            )
        return user


class UserProfileForm(forms.ModelForm):
    '''Form for updating entrepreneur profile and user details.'''
    first_name = forms.CharField(max_length=150, required=True, label="First Name")
    last_name = forms.CharField(max_length=150, required=False, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")

    class Meta:
        model = UserProfile
        fields = (
            "state",
            "district",
            "village_or_town",
            "preferred_language",
            "available_capital",
            "experience_years",
            "phone_number",
            "shg_or_fpo_member",
            "skills",
            "business_interests",
        )
        widgets = {
            "skills": forms.Textarea(attrs={"rows": 3}),
            "business_interests": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user_obj = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user_obj:
            self.fields["first_name"].initial = self.user_obj.first_name
            self.fields["last_name"].initial = self.user_obj.last_name
            self.fields["email"].initial = self.user_obj.email

    def clean_available_capital(self):
        val = self.cleaned_data.get("available_capital")
        if val is not None and val < Decimal("0.00"):
            raise ValidationError("Available capital cannot be negative.")
        return val

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user_obj:
            self.user_obj.first_name = self.cleaned_data.get("first_name", "")
            self.user_obj.last_name = self.cleaned_data.get("last_name", "")
            self.user_obj.email = self.cleaned_data.get("email", "")
            if commit:
                self.user_obj.save()
        if commit:
            profile.save()
        return profile
