"""
bids/forms.py
Form for placing a bid.
"""

from decimal import Decimal
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class BidForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(
            attrs={
                "step": "0.01",
                "placeholder": "0.00",
                "class": "bid-input",
            }
        ),
        label=_("Your Bid Amount"),
    )
