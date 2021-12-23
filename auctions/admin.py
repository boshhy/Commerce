from django.contrib import admin
from .models import User, Category, Listings, WatchList, Bids


# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listings)
admin.site.register(WatchList)
admin.site.register(Bids)
