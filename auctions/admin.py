from django.contrib import admin
from .models import User, Listings, Bids, Comments


class Listings_Admin(admin.ModelAdmin):
    list_display = ["title", "seller", "current_bid"]


class Bids_Admin(admin.ModelAdmin):
    list_display = ["amount", "user", "listing"]


admin.site.register(Listings, Listings_Admin)
admin.site.register(Bids, Bids_Admin)

# Register your models here.
admin.site.register(User)
# admin.site.register(Listings)
# admin.site.register(Bids)
admin.site.register(Comments)
