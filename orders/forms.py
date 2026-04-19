"""
orders/forms.py
Admin/staff forms for order management.
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Order


class AdvanceOrderForm(forms.Form):
    tracking_number = forms.CharField(
        required=False,
        max_length=100,
        label=_("Tracking Number"),
        help_text=_("Optional. Provide when advancing to SHIPPED."),
        widget=forms.TextInput(attrs={"placeholder": "1Z999AA10123456784"}),
    )


class UpdateTrackingForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["tracking_number", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
