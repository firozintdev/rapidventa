from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.OrderListView.as_view(), name="list"),
    path("<uuid:reference>/", views.OrderDetailView.as_view(), name="detail"),
    path("staff/all/", views.StaffOrderListView.as_view(), name="staff_list"),
]
