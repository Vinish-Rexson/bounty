from django.contrib import admin
from .models import CustomerProfile, Project, ProjectRequest, DeveloperRequest, MeetingRequest

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'industry', 'created_at']
    search_fields = ['user__username', 'company_name', 'industry']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'budget', 'status', 'assigned_developer', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description', 'customer__user__username']
    raw_id_fields = ['assigned_developer', 'required_skills']

@admin.register(ProjectRequest)
class ProjectRequestAdmin(admin.ModelAdmin):
    list_display = ['project', 'developer', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['project__title', 'developer__user__username', 'message']
    raw_id_fields = ['project', 'developer']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'project', 'developer', 'developer__user'
        )

@admin.register(DeveloperRequest)
class DeveloperRequestAdmin(admin.ModelAdmin):
    list_display = ['project', 'customer', 'developer', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project__title', 'customer__user__username', 'developer__user__username']
    raw_id_fields = ['project', 'customer', 'developer']

@admin.register(MeetingRequest)
class MeetingRequestAdmin(admin.ModelAdmin):
    list_display = ['customer', 'developer', 'status', 'scheduled_time', 'created_at']
    list_filter = ['status', 'created_at', 'scheduled_time']
    search_fields = ['customer__username', 'developer__user__username', 'message']
    raw_id_fields = ['customer', 'developer']
