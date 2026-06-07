from django.contrib import admin

from .models import Click, ShortURL

class ClickInLine(admin.TabularInline):
    model = Click
    extra = 0
    readonly_fields = ["clicked_at"]

@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ("short_code", "owner", "og_url", "click_count", "created_at")
    inlines = [ClickInLine]

@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ("short_url", "clicked_at")

