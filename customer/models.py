from django.db import models
from django.contrib.auth.models import User
from dev.models import Profile as DevProfile

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
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
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
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    developer = models.ForeignKey('dev.Profile', on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    initiated_by_customer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['project', 'developer']
        indexes = [
            models.Index(fields=['project', 'developer', 'status']),
        ]

    def __str__(self):
        return f"Request for {self.project.title} by {self.developer.display_name}"
