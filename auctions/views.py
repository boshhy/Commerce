from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import WatchList, Category, Bids
from .forms import ListingForm, BidForm
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
    is_bid_higher = False
    is_post = False

    # Check to see if the user is logged in and if the current listing being
    # viewed is on current users watchlist
    if request.user.is_authenticated:
        if WatchList.objects.filter(user=request.user, listings=listing):
            on_watchlist = True

    if request.method == "POST":
        is_post = True
        if "watchlist" in request.POST:
            is_post = False
            if not WatchList.objects.filter(user=request.user, listings=listing):
                watchlist = WatchList(user=request.user, listings=listing)
                watchlist.save()
                on_watchlist = True
            else:
                WatchList.objects.filter(
                    user=request.user, listings=listing).delete()
                on_watchlist = False

        if "bid" in request.POST:
            has_bids = Bids.objects.filter(listing=listing)

            # If current listing does not have any bids
            # Accept bids >= (greater than or equal to) current_bid
            if not has_bids:
                if float(request.POST.get("bid")) >= listing.current_bid:
                    listing.current_bid = request.POST.get('bid')
                    listing.save()
                    new_bid = Bids(amount=listing.current_bid,
                                   user=request.user, listing=listing)
                    new_bid.save()
                    is_bid_higher = True

            # If current listing already has some bids
            # Accept only bids > (greater than) current_bid
            elif float(request.POST.get("bid")) > listing.current_bid:
                listing.current_bid = request.POST.get('bid')
                listing.save()
                new_bid = Bids(amount=listing.current_bid,
                               user=request.user, listing=listing)
                new_bid.save()
                is_bid_higher = True

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "on_watchlist": on_watchlist,
                "bid_form": BidForm(),
                "is_bid_higher": is_bid_higher,
                "is_post": is_post
            })

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "on_watchlist": on_watchlist,
        "bid_form": BidForm(),
        "is_post": is_post
    })
