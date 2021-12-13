from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class auction_listings(models.Model):
    # title
    title = models.CharField(max_length=64, blank=False)
    # description
    description = models.TextField(blank=False)
    # seller
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings")
    # starting_bid
    starting_bid = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00)
    # current_bid
    Current_bid = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00)
    # category
    # TODO
    # active
    active = models.BooleanField(default=True)
    # image URL
    # TODO


class watch_list(models.Model):
    pass


class bids(models.Model):
    pass


class comments(models.Model):
    pass
