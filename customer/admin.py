from django.contrib import admin
from .models import CustomerProfile, Project, MeetingRequest, ProjectRequest, DeveloperRequest, ProjectStatusRequest

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'industry', 'created_at']
    search_fields = ['user__username', 'company_name', 'industry']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'budget', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description', 'customer__user__username']

@admin.register(MeetingRequest)
class MeetingRequestAdmin(admin.ModelAdmin):
    list_display = ['customer', 'developer', 'status', 'scheduled_time', 'created_at', 'is_active']
    list_filter = ['status', 'created_at', 'is_active']
    search_fields = ['customer__user__username', 'developer__user__username', 'message']
    readonly_fields = ['created_at', 'ended_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.ended_at:  # If meeting is ended
            return self.readonly_fields + ['ended_by', 'is_active']
        return self.readonly_fields

@admin.register(ProjectRequest)
class ProjectRequestAdmin(admin.ModelAdmin):
    list_display = ['project', 'developer', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project__title', 'developer__user__username', 'message']

@admin.register(DeveloperRequest)
class DeveloperRequestAdmin(admin.ModelAdmin):
    list_display = ['customer', 'developer', 'project', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__user__username', 'developer__user__username', 'project__title']

@admin.register(ProjectStatusRequest)
class ProjectStatusRequestAdmin(admin.ModelAdmin):
    list_display = ['project', 'requested_by', 'requested_status', 'is_approved', 'created_at']
    list_filter = ['requested_status', 'is_approved', 'created_at']
    search_fields = ['project__title', 'requested_by__username']
