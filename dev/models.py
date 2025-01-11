from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from django.core.exceptions import ValidationError

class Profile(models.Model):
    # Basic Info
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(
        max_length=50, 
        help_text="Name that will be shown to others",
        null=True, 
        blank=True
    )
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Professional Info
    title = models.CharField(max_length=100, help_text="e.g. Senior Full Stack Developer", null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    crypto_wallet_address = models.CharField(max_length=100, blank=True)
    

    skills = models.ManyToManyField('Skill', related_name='developers')
    
    # Social Links
    github_url = models.URLField(max_length=200, blank=True)
    linkedin_url = models.URLField(max_length=200, blank=True)
    portfolio_url = models.URLField(max_length=200, blank=True)

    
    # Availability
    is_available = models.BooleanField(default=False)
    available_from = models.TimeField(
        null=True, 
        blank=True,
        help_text="Your availability start time (in your timezone)"
    )
    available_to = models.TimeField(
        null=True, 
        blank=True,
        help_text="Your availability end time (in your timezone)"
    )
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Verification and Rating
    is_verified = models.BooleanField(default=False)
    rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('telegram', 'Telegram'),
            ('whatsapp', 'WhatsApp')
        ],
        default='email'
    )
    
    # Work Preferences
    min_project_duration = models.PositiveIntegerField(
        default=1,
        help_text="Minimum project duration in hours"
    )
    preferred_project_size = models.CharField(
        max_length=20,
        choices=[
            ('small', 'Small'),
            ('medium', 'Medium'),
            ('large', 'Large')
        ],
        default='medium'
    )
    
    # Additional Info
    certifications = models.ManyToManyField('Certification', blank=True)
    education = models.ManyToManyField('Education', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Add this field to your Profile model
    is_profile_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def clean(self):
        if self.available_from and self.available_to:
            if self.available_from >= self.available_to:
                raise ValidationError({
                    'available_to': 'End time must be after start time'
                })

class Skill(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Certification(models.Model):
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.name} from {self.issuing_organization}"

class Education(models.Model):
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    grade = models.CharField(max_length=50, blank=True)
    activities = models.TextField(blank=True)

    def __str__(self):
        return f"{self.degree} in {self.field_of_study} from {self.institution}"

class Review(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('profile', 'reviewer')

    def __str__(self):
        return f"Review for {self.profile.user.username} by {self.reviewer.username}"
    
