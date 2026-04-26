from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("admin-dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("how-to-bid/", views.HowToBidView.as_view(), name="how_to_bid"),
    path("how-to-sell/", views.HowToSellView.as_view(), name="how_to_sell"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("faq-question/", views.FaqQuestionView.as_view(), name="faq_question"),
]
