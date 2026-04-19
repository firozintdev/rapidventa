from django.contrib import admin
from .models import Bid


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "amount", "timestamp")
    list_filter = ("listing__status",)
    search_fields = ("user__email", "user__full_name", "listing__title")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)
