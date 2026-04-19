from django.urls import path
from . import views

app_name = "listings"

urlpatterns = [
    path("", views.ListingListView.as_view(), name="list"),
    path("listing/<int:pk>/", views.ListingDetailView.as_view(), name="detail"),
    path("listing/<int:pk>/review/", views.ReviewCreateView.as_view(), name="review"),
    path("listing/<int:pk>/buy-now/", views.BuyNowView.as_view(), name="buy_now"),
    path("listing/<int:pk>/watch/", views.ToggleWatchlistView.as_view(), name="toggle_watchlist"),
    path("listing/create/", views.ListingCreateView.as_view(), name="create"),
    path("listing/my/", views.MyListingsView.as_view(), name="my_listings"),
    path("listing/analytics/", views.SellerAnalyticsView.as_view(), name="analytics"),
    path("listing/upload/", views.CSVUploadView.as_view(), name="upload_csv"),
    path("watchlist/", views.WatchlistView.as_view(), name="watchlist"),
]
