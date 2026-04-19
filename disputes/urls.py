from django.urls import path
from . import views

app_name = "disputes"

urlpatterns = [
    path("raise/<uuid:reference>/", views.RaiseDisputeView.as_view(), name="raise"),
    path("<int:pk>/", views.DisputeDetailView.as_view(), name="detail"),
]
