"""
listings/views.py
Class-based views for auction listings.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, TemplateView

from core.mixins import SellerRequiredMixin
from core.models import AboutSection, FaqSection, HowItWorksSection
from .forms import CSVUploadForm, ListingFilterForm, ListingForm, ReviewForm
from .models import Listing, Watchlist
from .selectors import (
    get_active_listings,
    get_all_categories,
    get_featured_reviews,
    get_home_stats,
    get_listing_detail,
    get_listings_by_seller,
    get_seller_analytics,
    get_watchlist,
)
from .services import (
    add_listing_images,
    add_to_watchlist,
    bulk_upload_listings,
    buy_now_purchase,
    create_listing,
    create_review,
    remove_from_watchlist,
)


class ListingListView(View):
    """Public auction listing page with filter and search."""

    template_name = "listings/list.html"
    paginate_by = 12

    def get(self, request):
        form = ListingFilterForm(request.GET or None)
        category_slug = None
        order_by = "end_time"
        search_query = ""

        if form.is_valid():
            category = form.cleaned_data.get("category")
            category_slug = category.slug if category else None
            order_by = form.cleaned_data.get("order_by") or "end_time"
            search_query = form.cleaned_data.get("q", "")

        listings_qs = get_active_listings(
            category_slug=category_slug, order_by=order_by
        )

        if search_query:
            listings_qs = listings_qs.filter(title__icontains=search_query)

        paginator = Paginator(listings_qs, self.paginate_by)
        page_obj = paginator.get_page(request.GET.get("page"))

        return render(
            request,
            self.template_name,
            {
                "page_obj": page_obj,
                "filter_form": form,
                "categories": get_all_categories(),
                "about": AboutSection.get_solo(),
                "how_it_works": HowItWorksSection.get_solo(),
                "faq": FaqSection.get_solo(),
                "featured_reviews": get_featured_reviews(),
                **get_home_stats(),
            },
        )


class AuctionGridView(View):
    """Dedicated auction grid page with sidebar filters."""

    template_name = "listings/auction_grid.html"
    paginate_by = 12

    def get(self, request):
        form = ListingFilterForm(request.GET or None)
        category_slug = None
        order_by = "end_time"
        search_query = ""

        if form.is_valid():
            category = form.cleaned_data.get("category")
            category_slug = category.slug if category else None
            order_by = form.cleaned_data.get("order_by") or "end_time"
            search_query = form.cleaned_data.get("q", "")

        listings_qs = get_active_listings(
            category_slug=category_slug, order_by=order_by
        )

        if search_query:
            listings_qs = listings_qs.filter(title__icontains=search_query)

        paginator = Paginator(listings_qs, self.paginate_by)
        page_obj = paginator.get_page(request.GET.get("page"))

        return render(
            request,
            self.template_name,
            {
                "page_obj": page_obj,
                "filter_form": form,
                "categories": get_all_categories(),
                "total_count": paginator.count,
            },
        )


class ListingDetailView(View):
    """Auction detail page with bid history, tabs and reviews."""

    template_name = "listings/detail.html"

    def get(self, request, pk):
        listing = get_listing_detail(pk=pk)
        if not listing:
            from django.http import Http404
            raise Http404

        bids = listing.bids.select_related("user").order_by("-amount")[:10]
        reviews = listing.reviews.select_related("user").all()
        user_reviewed = (
            request.user.is_authenticated
            and listing.reviews.filter(user=request.user).exists()
        )
        is_watching = (
            request.user.is_authenticated
            and Watchlist.objects.filter(user=request.user, listing=listing).exists()
        )
        related = (
            get_active_listings(category_slug=listing.category.slug)
            .exclude(pk=listing.pk)[:8]
        )
        return render(
            request,
            self.template_name,
            {
                "listing": listing,
                "bids": bids,
                "reviews": reviews,
                "review_form": ReviewForm(),
                "user_reviewed": user_reviewed,
                "is_watching": is_watching,
                "related": related,
            },
        )


class ReviewCreateView(LoginRequiredMixin, View):
    """Submit a review for a listing."""

    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                create_review(
                    listing=listing,
                    user=request.user,
                    **form.cleaned_data,
                )
                messages.success(request, "Your review has been submitted. Thank you!")
            except ValidationError as exc:
                messages.error(request, str(exc))
        else:
            messages.error(request, "Please correct the errors in your review.")
        return redirect(listing.get_absolute_url() + "#reviews")


class ListingCreateView(SellerRequiredMixin, View):
    """Seller creates a new listing (saved as PENDING)."""

    template_name = "listings/create.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ListingForm()})

    def post(self, request):
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                listing = create_listing(
                    seller=request.user,
                    **{k: form.cleaned_data[k] for k in form.cleaned_data},
                )
                images = request.FILES.getlist("images")
                if images:
                    add_listing_images(listing=listing, images=images)
                messages.success(
                    request,
                    f'Listing "{listing.title}" submitted for admin approval.',
                )
                return redirect("listings:my_listings")
            except (PermissionDenied, ValidationError) as exc:
                form.add_error(None, str(exc))

        return render(request, self.template_name, {"form": form})


class MyListingsView(SellerRequiredMixin, TemplateView):
    """Seller's own listing dashboard."""

    template_name = "listings/my_listings.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["listings"] = get_listings_by_seller(seller=self.request.user)
        return ctx


class SellerAnalyticsView(SellerRequiredMixin, TemplateView):
    """Seller dashboard showing listing stats, bid counts, revenue and recent activity."""

    template_name = "listings/analytics.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(get_seller_analytics(seller=self.request.user))
        return ctx


class WatchlistView(LoginRequiredMixin, TemplateView):
    """Display all listings the authenticated user is watching."""

    template_name = "listings/watchlist.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["watchlist_entries"] = get_watchlist(user=self.request.user)
        return ctx


class BuyNowView(LoginRequiredMixin, View):
    """POST-only: purchase a listing immediately at its buy_now_price."""

    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        try:
            order = buy_now_purchase(user=request.user, listing=listing)
            messages.success(
                request,
                f'Purchase confirmed! Your order reference is {order.short_reference}. '
                f'The auction house will contact you to arrange payment and delivery.',
            )
            return redirect(order.get_absolute_url())
        except (PermissionDenied, ValidationError) as exc:
            messages.error(request, str(exc))
            return redirect(listing.get_absolute_url())


class ToggleWatchlistView(LoginRequiredMixin, View):
    """POST-only: add to watchlist if not watching, remove if already watching."""

    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        is_watching = Watchlist.objects.filter(user=request.user, listing=listing).exists()

        if is_watching:
            remove_from_watchlist(user=request.user, listing=listing)
            messages.success(request, f'"{listing.title}" removed from your watchlist.')
        else:
            add_to_watchlist(user=request.user, listing=listing)
            messages.success(request, f'"{listing.title}" added to your watchlist.')

        return redirect(listing.get_absolute_url())


class CSVUploadView(SellerRequiredMixin, View):
    """Bulk listing upload via CSV file."""

    template_name = "listings/upload_csv.html"

    def get(self, request):
        return render(request, self.template_name, {"form": CSVUploadForm()})

    def post(self, request):
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                result = bulk_upload_listings(
                    seller=request.user,
                    csv_file=request.FILES["csv_file"],
                )
                messages.success(
                    request,
                    f"{result['created']} listing(s) created. "
                    f"{len(result['errors'])} error(s).",
                )
                return render(
                    request,
                    self.template_name,
                    {"form": CSVUploadForm(), "result": result},
                )
            except PermissionDenied as exc:
                form.add_error(None, str(exc))

        return render(request, self.template_name, {"form": form})
