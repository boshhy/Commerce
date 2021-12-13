from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    pass


class auction_listings(models.Model):
    # title
    title = models.CharField(max_length=64, blank=False)
    # description
    description = models.CharField(blank=False)
    # seller
    seller = models.ForeignKey(
        User, on_delete=CASCADE, related_name="listings")
    # starting_bid
    # current_bid
    # category
    # active
    # image URL
    pass


class watch_list(models.Model):
    pass


class bids(models.Model):
    pass


class comments(models.Model):
    pass
