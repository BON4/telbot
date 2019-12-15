from django import forms
from .models import Store


class StoreForm(forms.ModelForm):
    long = forms.DecimalField(max_digits=22, decimal_places=16, blank=True, null=False)
    lat = forms.DecimalField(max_digits=22, decimal_places=16, blank=True, null=False)

    class Meta:
        model = Store
        fields = ('id', 'store_name', 'street_name', 'latitude', 'longitude')

