from django.contrib import admin
from .models import Spam

@admin.register(Spam)
class SpamAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone_number', 'marked_by')
