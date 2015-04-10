from django.contrib import admin
from .models import Settings


class SettingsAdmin(admin.ModelAdmin):
    list_display = ('namespace', 'key', 'value')
    list_filter = ('namespace', )
    search_fields = ('key', 'value')

admin.site.register(Settings, SettingsAdmin)
