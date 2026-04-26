"""
core/views.py
Platform-level views (staff-only admin dashboard, etc.).
"""

from django import forms
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from core.mixins import StaffRequiredMixin
from core.models import FaqSection
from core.selectors import get_platform_stats


class FaqContactForm(forms.Form):
    email   = forms.EmailField(label="Your email")
    message = forms.CharField(label="Message", widget=forms.Textarea)


class AdminDashboardView(StaffRequiredMixin, TemplateView):
    """Platform-wide analytics dashboard, visible to staff only."""

    template_name = "core/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(get_platform_stats())
        return ctx


class HowToBidView(TemplateView):
    template_name = "core/how_to_bid.html"


class HowToSellView(TemplateView):
    template_name = "core/how_to_sell.html"


class ContactView(TemplateView):
    template_name = "core/contact.html"


class FaqQuestionView(View):
    """Handles the 'Any Question?' form on the homepage FAQ section."""

    def post(self, request):
        form = FaqContactForm(request.POST)
        if form.is_valid():
            faq = FaqSection.get_solo()
            sender  = form.cleaned_data["email"]
            message = form.cleaned_data["message"]
            try:
                send_mail(
                    subject=f"FAQ Question from {sender}",
                    message=f"From: {sender}\n\n{message}",
                    from_email=sender,
                    recipient_list=[faq.contact_email],
                    fail_silently=False,
                )
                messages.success(request, "Your question has been sent. We'll get back to you soon!")
            except Exception:
                messages.error(request, "Sorry, we couldn't send your message. Please try again later.")
        else:
            messages.error(request, "Please enter a valid email address and message.")
        return redirect(request.META.get("HTTP_REFERER", "/") + "#faq-section")
