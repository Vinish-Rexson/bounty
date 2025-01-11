from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Skill, Project, Comment

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'created_at', 'view_live_link', 'view_github_link')
    search_fields = ('name', 'client', 'readme')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    def view_live_link(self, obj):
        if obj.deployed_url:
            return format_html('<a href="{}" target="_blank">View Live</a>', obj.deployed_url)
        return '-'
    view_live_link.short_description = 'Live Site'

    def view_github_link(self, obj):
        if obj.github_url:
            return format_html('<a href="{}" target="_blank">View Code</a>', obj.github_url)
        return '-'
    view_github_link.short_description = 'GitHub'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'display_name', 
        'title',
        'is_verified', 
        'is_available',
        'hourly_rate',
        'years_of_experience',
        'project_count'
    )
    list_filter = (
        'is_verified', 
        'is_available', 
        'preferred_project_size',
        'created_at'
    )
    search_fields = (
        'user__username', 
        'user__email',
        'display_name', 
        'bio',
        'title'
    )
    filter_horizontal = ('skills',)
    readonly_fields = ('created_at', 'updated_at')
    
    def project_count(self, obj):
        return obj.project_set.count()
    project_count.short_description = 'Projects'

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user', 
                'display_name', 
                'profile_picture', 
                'bio',
                'title'
            )
        }),
        ('Professional Details', {
            'fields': (
                'years_of_experience',
                'hourly_rate',
                'skills',
                'preferred_project_size',
                'min_project_duration'
            )
        }),
        ('Contact & Links', {
            'fields': (
                'preferred_contact_method',
                'github_url',
                'linkedin_url',
                'portfolio_url',
                'crypto_wallet_address'
            )
        }),
        ('Availability', {
            'fields': (
                'is_available',
                'timezone',
                'availability_type',
                ('weekday_from', 'weekday_to'),
                ('weekend_from', 'weekend_to'),
                ('temp_from', 'temp_to')
            )
        }),
        ('Status', {
            'fields': (
                'is_verified',
                'created_at',
                'updated_at'
            )
        })
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('profile', 'author', 'created_at')
    search_fields = ('content', 'author__username', 'profile__user__username')
    ordering = ('-created_at',)
