from django.contrib import admin
from .models import Profile, Message
#from .forms import StoreForm


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'name')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'text', 'date_of_creation')

    def get_queryset(self, request):
        qs = super(MessageAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
# Register your models here.