from django import forms
from django.utils.translation import gettext_lazy as _


class RaiseDisputeForm(forms.Form):
    reason = forms.CharField(
        label=_("Reason for dispute"),
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "Describe the issue in detail…",
                "class": "form-control rv-input",
            }
        ),
        min_length=20,
        error_messages={"min_length": _("Please provide at least 20 characters.")},
    )
