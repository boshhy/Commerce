from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import WatchList, Category
from .forms import ListingForm
from django.contrib.auth.decorators import login_required

from .models import Listings, User


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.all(),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="login")
def add_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            imageURL = form.cleaned_data["imageURL"]
            category = Category(name=form.cleaned_data["category"])

            if not Category.objects.filter(name=category):
                category.save()
            else:
                category = Category.objects.get(name=category)

            new_listing = Listings(title=title, description=description,
                                   seller=request.user, current_bid=starting_bid, category=category, imageURL=imageURL)
            new_listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            # need to give invalid form back to user for fixing
            pass
    else:
        return render(request, "auctions/new.html", {
            "form": ListingForm()
        })


def listing(request, listing_id):
    listing = Listings.objects.get(pk=int(listing_id))
    on_watchlist = False
    if request.user.is_authenticated:
        if WatchList.objects.filter(user=request.user, listings=listing):
            on_watchlist = True
    if request.method == "POST":
        if "watchlist" in request.POST:
            if not WatchList.objects.filter(user=request.user, listings=listing):
                watchlist = WatchList(user=request.user, listings=listing)
                watchlist.save()
                on_watchlist = True
            else:
                WatchList.objects.filter(
                    user=request.user, listings=listing).delete()
                on_watchlist = False
        if "bid" in request.POST:
            if int(request.POST.get("bid")) > listing.current_bid:
                listing.current_bid = request.POST.get('bid')
                listing.save()
            return render(request, "auctions/test.html", {
                "test": listing.current_bid
            })

    return render(request, "auctions/listing.html", {
        "test": listing,
        "on_watchlist": on_watchlist
    })
