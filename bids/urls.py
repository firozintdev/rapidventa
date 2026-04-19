from django.urls import path
from . import views

app_name = "bids"

urlpatterns = [
    path("place/<int:pk>/", views.PlaceBidView.as_view(), name="place"),
]
