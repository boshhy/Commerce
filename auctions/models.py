from typing import List
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import NullBooleanField, related
from django import forms


class User(AbstractUser):
    pass


class Category(models.Model):
    UNKNOWN = 'Unknown'
    APPLIANCES = 'Appliances'
    APPS = 'Apps'
    ARTS = 'Arts'
    AUTO = 'Automotive'
    BABY = 'Baby'
    BEAUTY = 'Beauty'
    BOOKS = 'Books'
    CDS = 'CDs'
    CELL_PHONES = 'Cell'
    CLOTHING = 'Clothing'
    COLLECTIBLES = 'Collectibles'
    COMPUTERS = 'Computers'
    ELECTRONICS = 'Electronics'
    GARDEN = 'Garden'
    GROCERY = 'Grocery'
    HANDMADE = 'Handmade'
    HEALTH = 'Health'
    HOME = 'Home'
    INDUSTRIAL = 'Industrial'
    LUGGAGE = 'Luggage'
    MOVIES = 'Movies'
    MUSICAL = 'Musical'
    OFFICE = 'Office'
    PET = 'Pet'
    SPORTS = 'Sports'
    TOOLS = 'Tools'
    TOYS = 'Toys'
    VIDEO_GAMES = 'Video'

    choices = [
        (UNKNOWN, "Unknown"),
        (APPLIANCES, 'Appliances'),
        (APPS, 'apps & Games'),
        (ARTS, 'Arts, Crafts, & Sewing'),
        (AUTO, 'Automotive Parts & Accessories'),
        (BABY, 'Baby'),
        (BEAUTY, 'Beauty & Personal Care'),
        (BOOKS, 'Books'),
        (CDS, 'CDs & Vinyl'),
        (CELL_PHONES, 'Cell Phones & Accessories'),
        (CLOTHING, 'Clothing, Shoes and Jewelry'),
        (COLLECTIBLES, 'Collectibles & Fine Art'),
        (COMPUTERS, 'Computers'),
        (ELECTRONICS, 'Electronics'),
        (GARDEN, 'Garden & Outdoor'),
        (GROCERY, 'Grocery & Gourmet Food'),
        (HANDMADE, 'Handmade'),
        (HEALTH, 'Health, Household & Baby Care'),
        (HOME, 'Home & Kitchen'),
        (INDUSTRIAL, 'Industrial & Scientific'),
        (LUGGAGE, 'Luggage & Travel Gear'),
        (MOVIES, 'Movies & TV'),
        (MUSICAL, 'Musical Instruments'),
        (OFFICE, 'Office Products'),
        (PET, 'Pet Supplies'),
        (SPORTS, 'Sports & Outdoors'),
        (TOOLS, 'Tools & Home Improvement'),
        (TOYS, 'Toys & Games'),
        (VIDEO_GAMES, 'Video Games'),
    ]

    name = models.CharField(max_length=64, choices=choices, blank=False,
                            default=UNKNOWN)

    def __str__(self):
        return self.name


class ListingForm(forms.Form):
    title = forms.CharField(max_length=64)
    description = forms.CharField(widget=forms.Textarea())
    starting_bid = forms.DecimalField(max_digits=16, decimal_places=2)
    # category = forms.CharField(max_length=64, required=False)
    category = forms.ChoiceField(
        widget=forms.Select(), choices=Category.choices)
    imageURL = forms.CharField(max_length=1024, required=False)


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
        User, on_delete=models.CASCADE, related_name="watchlist", blank=False)
    listings = models.ForeignKey(
        Listings, on_delete=models.CASCADE, related_name="watchlist", blank=False)

    def __str__(self):
        return f"{self.user} {self.listings}"


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
