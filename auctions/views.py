from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import WatchList, Category, Bids, Comments
from .forms import ListingForm, BidForm, CommentForm
from django.contrib.auth.decorators import login_required

from .models import Listings, User


def index(request):
    # might want to only display the active listings
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.filter(active=True),
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
            if not imageURL:
                imageURL = "https://t3.ftcdn.net/jpg/04/34/72/82/360_F_434728286_OWQQvAFoXZLdGHlObozsolNeuSxhpr84.jpg"
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
    try:
        listing = Listings.objects.get(pk=int(listing_id))
    except Listings.DoesNotExist:
        return render(request, "auctions/listing_deleted.html")
    if listing.active == False:
        return redirect("inactive", listing_id)
    comments = Comments.objects.filter(listing=listing)
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

        elif "bid" in request.POST:
            has_bids = Bids.objects.filter(listing=listing)

            # If current listing does not have any bids
            # Accept bids >= (greater than or equal to) current_bid
            if not has_bids:
                if float(request.POST.get("bid")) >= listing.current_bid:
                    listing.current_bid = request.POST.get('bid')
                    listing.buyer = request.user
                    listing.save()
                    new_bid = Bids(amount=listing.current_bid,
                                   user=request.user, listing=listing)
                    new_bid.save()
                    is_bid_higher = True

            # If current listing already has some bids
            # Accept only bids > (greater than) current_bid
            elif float(request.POST.get("bid")) > listing.current_bid:
                listing.current_bid = request.POST.get('bid')
                listing.buyer = request.user
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
                "is_post": is_post,
                "comment_form": CommentForm(),
                "comments": comments,
            })

        elif "comment" in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.cleaned_data["comment"]
                new_comment = Comments(
                    user=request.user, comment=comment, listing=listing)
                new_comment.save()

                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "on_watchlist": on_watchlist,
                    "bid_form": BidForm(),
                    "is_post": False,
                    "comment_form": CommentForm(),
                    "comments": comments,
                })
            return HttpResponse("Something went wrong: Invalid Comment Form")

        elif "end_listing" in request.POST:
            listing.active = False
            listing.save()
            return redirect("inactive", listing_id)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "on_watchlist": on_watchlist,
        "bid_form": BidForm(),
        "is_post": is_post,
        "comment_form": CommentForm(),
        "comments": comments,
    })


def inactive(request, listing_id):
    has_won = False
    on_watchlist = False
    try:
        listing = Listings.objects.get(pk=int(listing_id))
    except Listings.DoesNotExist:
        return render(request, "auctions/listing_deleted.html")
    listing = Listings.objects.get(pk=int(listing_id))
    if listing.active == True:
        return redirect("listing", listing_id)
    if listing.buyer == request.user:
        has_won = True
    comments = Comments.objects.filter(listing=listing)
    if WatchList.objects.filter(user=request.user, listings=listing):
        on_watchlist = True

    if request.method == "POST":
        on_watchlist = False
        if "watchlist" in request.POST:
            WatchList.objects.filter(
                user=request.user, listings=listing).delete()
            return render(request, "auctions/inactive_listing.html", {
                "listing": listing,
                "comments": comments,
                "has_won": has_won,
                "on_watchlist": on_watchlist,
            })

    return render(request, "auctions/inactive_listing.html", {
        "listing": listing,
        "comments": comments,
        "has_won": has_won,
        "on_watchlist": on_watchlist,
    })


def watchlist(request):
    watchlist = WatchList.objects.filter(
        user=request.user, listings__active=True)
    watchlist_inactive = WatchList.objects.filter(
        user=request.user, listings__active=False)
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist,
        "watchlist_inactive": watchlist_inactive,
    })


def categories(request):
    choices = Category.choices
    return render(request, "auctions/categories.html", {
        "choices": choices,
    })


def category(request, category):
    listings = Listings.objects.filter(category__name=category, active=True)
    if listings:
        return render(request, "auctions/category.html", {
            "category": category,
            "listings": listings,
        })

    return render(request, "auctions/no_items.html", {
        "category": category,
    })
