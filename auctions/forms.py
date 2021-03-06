from django import forms
from .models import Category, Bids


class ListingForm(forms.Form):
    title = forms.CharField(max_length=64)
    description = forms.CharField(widget=forms.Textarea())
    starting_bid = forms.DecimalField(max_digits=16, decimal_places=2)
    # category = forms.CharField(max_length=64, required=False)
    category = forms.ChoiceField(
        widget=forms.Select(), choices=Category.choices)
    imageURL = forms.CharField(max_length=1024, required=False)


class BidForm(forms.Form):
    bid = forms.DecimalField(max_digits=16, decimal_places=2)


class CommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 64}))
