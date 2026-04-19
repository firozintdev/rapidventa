"""
accounts/views.py
Class-based views for authentication, registration, and profile management.
Business logic is delegated to accounts/services.py.
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView, TemplateView

from .forms import LoginForm, ProfileUpdateForm, RegistrationForm
from .services import register_user, update_profile
from .selectors import get_user_by_id, get_won_auctions, get_lost_auctions, get_void_auctions, get_seller_public_profile
from bids.selectors import get_bids_by_user
from listings.selectors import get_listings_by_seller
from orders.selectors import get_orders_by_buyer


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return render(request, self.template_name, {"form": RegistrationForm()})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = register_user(
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password"],
                    full_name=form.cleaned_data["full_name"],
                    phone=form.cleaned_data.get("phone", ""),
                    address=form.cleaned_data.get("address", ""),
                    national_id=form.cleaned_data.get("national_id", ""),
                    role=form.cleaned_data["role"],
                )
                login(request, user)
                messages.success(
                    request,
                    "Welcome to RapidVenta! Your account is pending admin validation "
                    "before you can place bids.",
                )
                return redirect("accounts:dashboard")
            except ValidationError as exc:
                form.add_error(None, exc)

        return render(request, self.template_name, {"form": form})


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("accounts:dashboard")


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect("listings:list")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["recent_bids"] = get_bids_by_user(user=user)[:5]
        ctx["recent_orders"] = get_orders_by_buyer(buyer=user)[:5]
        ctx["is_profile_complete"] = user.is_profile_complete
        if user.is_seller:
            ctx["my_listings"] = get_listings_by_seller(seller=user)[:5]
        return ctx


class ProfileView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"

    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            update_profile(
                user=request.user,
                full_name=form.cleaned_data["full_name"],
                phone=form.cleaned_data["phone"],
                address=form.cleaned_data["address"],
                national_id=form.cleaned_data["national_id"],
            )
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
        return render(request, self.template_name, {"form": form})


class SellerProfileView(View):
    """Public seller profile — no login required."""

    template_name = "accounts/seller_profile.html"

    def get(self, request, pk):
        from django.http import Http404
        data = get_seller_public_profile(seller_id=pk)
        if data is None:
            raise Http404
        return render(request, self.template_name, data)


class AuctionHistoryView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/auction_history.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["all_bids"] = get_bids_by_user(user=user)
        ctx["won_bids"] = get_won_auctions(user=user)
        ctx["lost_bids"] = get_lost_auctions(user=user)
        ctx["void_bids"] = get_void_auctions(user=user)
        return ctx
