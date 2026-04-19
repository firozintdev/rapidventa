"""
accounts/forms.py
Forms for user authentication and profile management.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegistrationForm(forms.Form):
    """New user registration form."""

    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "Jane Doe"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "jane@example.com"}),
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "+1 555 000 0000"}),
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Street, City, Country"}),
    )
    national_id = forms.CharField(
        max_length=100,
        required=False,
        label=_("National ID / Document"),
        widget=forms.TextInput(attrs={"placeholder": "Passport / National ID"}),
    )
    role = forms.ChoiceField(
        choices=[
            (role, label)
            for role, label in User.Role.choices
            if role != User.Role.ADMIN
        ],
        initial=User.Role.BUYER,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
        min_length=8,
    )
    password_confirm = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password_confirm"):
            raise forms.ValidationError(_("Passwords do not match."))
        return cleaned

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("This email is already registered."))
        return email


class LoginForm(AuthenticationForm):
    """Custom login form with styled widgets."""

    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={"autofocus": True, "placeholder": "jane@example.com"}
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"})
    )


class ProfileUpdateForm(forms.ModelForm):
    """Allow users to edit their own profile (safe fields only)."""

    class Meta:
        model = User
        fields = ["full_name", "phone", "address", "national_id"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }
