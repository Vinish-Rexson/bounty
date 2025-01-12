from django.contrib import admin
from django.forms import Select
from django.db import models
from .models import CustomerProfile, Project, ProjectRequest, DeveloperRequest, MeetingRequest, ProjectStatusRequest

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'industry', 'created_at']
    search_fields = ['user__username', 'company_name', 'industry']
    list_select_related = ['user']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'budget', 'status', 'assigned_developer', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description', 'customer__user__username']
    raw_id_fields = ['customer', 'assigned_developer']
    filter_horizontal = ['required_skills']
    formfield_overrides = {
        models.CharField: {'widget': Select(choices=Project.STATUS_CHOICES)},
    }

@admin.register(ProjectRequest)
class ProjectRequestAdmin(admin.ModelAdmin):
    list_display = ['project', 'developer', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project__title', 'developer__user__username']
    raw_id_fields = ['project', 'developer']
    readonly_fields = ['created_at', 'updated_at']
    formfield_overrides = {
        models.CharField: {'widget': Select(choices=ProjectRequest.STATUS_CHOICES)},
    }

@admin.register(DeveloperRequest)
class DeveloperRequestAdmin(admin.ModelAdmin):
    list_display = ['project', 'customer', 'developer', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project__title', 'customer__user__username', 'developer__user__username']
    raw_id_fields = ['project', 'customer', 'developer']
    readonly_fields = ['created_at', 'updated_at']
    formfield_overrides = {
        models.CharField: {'widget': Select(choices=DeveloperRequest.STATUS_CHOICES)},
    }

@admin.register(MeetingRequest)
class MeetingRequestAdmin(admin.ModelAdmin):
    list_display = ['customer', 'developer', 'status', 'scheduled_time', 'created_at']
    list_filter = ['status', 'created_at', 'scheduled_time']
    search_fields = ['customer__user__username', 'developer__user__username']
    raw_id_fields = ['customer', 'developer']
    readonly_fields = ['created_at']
    formfield_overrides = {
        models.CharField: {'widget': Select(choices=MeetingRequest.STATUS_CHOICES)},
    }

@admin.register(ProjectStatusRequest)
class ProjectStatusRequestAdmin(admin.ModelAdmin):
    list_display = ['project', 'requested_by', 'requested_status', 'is_approved', 'created_at']
    list_filter = ['requested_status', 'is_approved', 'created_at']
    search_fields = ['project__title', 'requested_by__username']
    raw_id_fields = ['project', 'requested_by']
    readonly_fields = ['created_at']
    formfield_overrides = {
        models.CharField: {'widget': Select(choices=ProjectStatusRequest.STATUS_CHOICES)},
    }
