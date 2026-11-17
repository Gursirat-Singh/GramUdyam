from django.contrib import admin
from accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "state", "district", "village_or_town", "available_capital", "preferred_language")
    list_filter = ("state", "preferred_language", "shg_or_fpo_member")
    search_fields = ("user__username", "district", "village_or_town", "skills")
