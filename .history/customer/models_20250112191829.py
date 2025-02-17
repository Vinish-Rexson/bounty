from django.db import models
from django.contrib.auth.models import User
from dev.models import Profile as DevProfile
from django.utils import timezone
from django.db.models import JSONField

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Customer Profile"

class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('payment_processing', 'Payment Processing'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.ManyToManyField('dev.Skill')
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in hours")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_developer = models.ForeignKey(DevProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    interested_developers = models.ManyToManyField(DevProfile, through='ProjectRequest', related_name='interested_projects')

    def __str__(self):
        return self.title

class ProjectRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('payment_pending', 'Payment Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='requests')
    developer = models.ForeignKey('dev.Profile', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(help_text="Message to the customer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('project', 'developer')
    
    def save(self, *args, **kwargs):
        # Update project status based on request status
        if self.status == 'accepted':
            self.project.status = 'payment_processing'
            self.project.assigned_developer = self.developer
            self.project.save()
        elif self.status == 'payment_pending':
            self.project.status = 'payment_processing'
            self.project.save()
        elif self.status == 'in_progress':
            self.project.status = 'in_progress'
            self.project.save()
        elif self.status == 'completed':
            self.project.status = 'completed'
            self.project.save()
        elif self.status == 'cancelled':
            self.project.status = 'cancelled'
            self.project.save()
            
        super().save(*args, **kwargs)

class DeveloperRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('payment_pending', 'Payment Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    developer = models.ForeignKey('dev.Profile', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(help_text="Message to the developer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('project', 'developer', 'customer')
    
    def save(self, *args, **kwargs):
        # Update project status based on request status
        if self.status == 'accepted':
            self.project.status = 'payment_processing'
            self.project.assigned_developer = self.developer
            self.project.save()
        elif self.status == 'payment_pending':
            self.project.status = 'payment_processing'
            self.project.save()
        elif self.status == 'in_progress':
            self.project.status = 'in_progress'
            self.project.save()
        elif self.status == 'completed':
            self.project.status = 'completed'
            self.project.save()
        elif self.status == 'cancelled':
            self.project.status = 'cancelled'
            self.project.save()
            
        super().save(*args, **kwargs)

class MeetingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ]
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    developer = models.ForeignKey('dev.Profile', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(help_text="Message for the meeting")
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    room_id = models.CharField(max_length=100, null=True, blank=True)
    meeting_url = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    ended_by = models.CharField(max_length=20, choices=[
        ('customer', 'Customer'),
        ('developer', 'Developer')
    ], null=True, blank=True)
    end_reason = models.CharField(max_length=50, null=True, blank=True)
    duration = models.IntegerField(default=0)  # Duration in seconds
    participant_count = models.IntegerField(default=0)
    screen_shares = models.IntegerField(default=0)
    mic_toggles = models.IntegerField(default=0)
    camera_toggles = models.IntegerField(default=0)
    chat_messages = models.IntegerField(default=0)
    stats = JSONField(null=True, blank=True)
    
    def end_meeting(self, ended_by, stats=None):
        self.is_active = False
        self.ended_at = timezone.now()
        self.ended_by = ended_by
        
        # Update meeting statistics if provided
        if stats:
            self.duration = stats.get('duration', 0)
            self.participant_count = stats.get('participant_count', 0)
            self.screen_shares = stats.get('screen_shares', 0)
            self.mic_toggles = stats.get('mic_toggles', 0)
            self.camera_toggles = stats.get('camera_toggles', 0)
            self.chat_messages = stats.get('chat_messages', 0)
        
        self.save()

class ProjectStatusRequest(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    REQUESTER_CHOICES = [
        ('customer', 'Customer'),
        ('developer', 'Developer')
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_requests')
    requested_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    requester_type = models.CharField(max_length=20, choices=REQUESTER_CHOICES)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
