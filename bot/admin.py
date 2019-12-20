from django.contrib import admin
from .models import Profile, Message, Store, Product
#from .forms import StoreForm


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'product_code')


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    fields = ['store_name', 'street_name', 'latitude', 'longitude', 'product']
    list_display = ('id', 'store_name', 'street_name', 'latitude', 'get_products', 'longitude')

    def get_products(self, obj):
        return "\n".join([str(p.product_code) for p in obj.product.all()])


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'store', 'text', 'date_of_creation')

    def get_queryset(self, request):
        qs = super(MessageAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
