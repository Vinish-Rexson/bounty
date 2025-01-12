from django.contrib import admin
from django.forms import Select, ModelChoiceField
from django.db import models
from .models import CustomerProfile, Project, ProjectRequest, DeveloperRequest, MeetingRequest, ProjectStatusRequest, MeetingRequest, ProjectRequest, DeveloperRequest, ProjectStatusRequest

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
    raw_id_fields = ['customer']
    filter_horizontal = ['required_skills']
    formfield_overrides = {
        models.CharField: {'widget': Select(choices=Project.STATUS_CHOICES)},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_developer":
            return ModelChoiceField(
                queryset=db_field.related_model.objects.all(),
                widget=Select(),
                required=False
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(ProjectRequest)
class ProjectRequestAdmin(admin.ModelAdmin):
    list_display = ['project', 'developer', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project__title', 'developer__user__username']
    raw_id_fields = ['project']
    readonly_fields = ['created_at', 'updated_at']
    formfield_overrides = {
        models.CharField: {'widget': Select(choices=ProjectRequest.STATUS_CHOICES)},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "developer":
            return ModelChoiceField(
                queryset=db_field.related_model.objects.all(),
                widget=Select(),
                required=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(DeveloperRequest)
class DeveloperRequestAdmin(admin.ModelAdmin):
    list_display = ['project', 'customer', 'developer', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project__title', 'customer__user__username', 'developer__user__username']
    raw_id_fields = ['project']
    readonly_fields = ['created_at', 'updated_at']
    formfield_overrides = {
        models.CharField: {'widget': Select(choices=DeveloperRequest.STATUS_CHOICES)},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["developer", "customer"]:
            return ModelChoiceField(
                queryset=db_field.related_model.objects.all(),
                widget=Select(),
                required=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(MeetingRequest)
class MeetingRequestAdmin(admin.ModelAdmin):
    list_display = ['customer', 'developer', 'status', 'scheduled_time', 'created_at']
    list_filter = ['status', 'created_at', 'scheduled_time']
    search_fields = ['customer__user__username', 'developer__user__username']
    readonly_fields = ['created_at']
    formfield_overrides = {
        models.CharField: {'widget': Select(choices=MeetingRequest.STATUS_CHOICES)},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["developer", "customer"]:
            return ModelChoiceField(
                queryset=db_field.related_model.objects.all(),
                widget=Select(),
                required=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(ProjectStatusRequest)
class ProjectStatusRequestAdmin(admin.ModelAdmin):
    list_display = ['project', 'requested_by', 'requested_status', 'is_approved', 'created_at']
    list_filter = ['requested_status', 'is_approved', 'created_at']
    search_fields = ['project__title', 'requested_by__username']
    readonly_fields = ['created_at']
    formfield_overrides = {
        models.CharField: {'widget': Select(choices=ProjectStatusRequest.STATUS_CHOICES)},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["project", "requested_by"]:
            return ModelChoiceField(
                queryset=db_field.related_model.objects.all(),
                widget=Select(),
                required=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
