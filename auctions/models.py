from typing import List
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import related
from django import forms


class ListingForm(forms.Form):
    title = forms.CharField(max_length=64)
    description = forms.CharField(widget=forms.Textarea())
    starting_bid = forms.DecimalField(max_digits=16, decimal_places=2)
    category = forms.CharField(max_length=64, required=False)
    imageURL = forms.CharField(max_length=1024, required=False)


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64, blank=False, default="Unknown")

    def __str__(self):
        return self.name


class Listings(models.Model):
    title = models.CharField(max_length=64, blank=False)
    description = models.TextField(blank=False)
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings")
    new_bid = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00)
    current_bid = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="listings")
    active = models.BooleanField(default=True)
    # image URL
    imageURL = models.CharField(max_length=1024)
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="purchase_history", blank=True, null=True)

    def __str__(self):
        return f"{self.title} \nseller:{self.seller} \ncurrent bid:{self.current_bid} \nactive:{self.active} \nbuyer:{self.buyer}"


class WatchList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="watchlist")
    listings = models.ForeignKey(
        Listings, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return self.listings


class Bids(models.Model):
    amount = models.DecimalField(max_digits=16, decimal_places=2, blank=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids", blank=False)
    listing = models.ForeignKey(
        Listings, on_delete=models.CASCADE, related_name="bids", blank=False)

    def __str__(self):
        return self.bid


class Comments(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments", blank=False)
    comment = models.TextField()
    listing = models.ForeignKey(
        Listings, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return self.comment
