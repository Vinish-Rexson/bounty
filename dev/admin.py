from django.contrib import admin
from .models import Profile, Skill

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'is_verified', 'is_profile_completed')
    search_fields = ('user__username', 'display_name')
