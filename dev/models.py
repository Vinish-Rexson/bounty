from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    
    # Weekday availability
    weekday_from = models.TimeField(
        null=True, blank=True,
        help_text="Your weekday availability start time"
    )
    weekday_to = models.TimeField(
        null=True, blank=True,
        help_text="Your weekday availability end time"
    )
    
    # Weekend availability
    weekend_from = models.TimeField(
        null=True, blank=True,
        help_text="Your weekend availability start time"
    )
    weekend_to = models.TimeField(
        null=True, blank=True,
        help_text="Your weekend availability end time"
    )
    
    # Temporary availability
    temp_from = models.TimeField(
        null=True, blank=True,
        help_text="Your temporary availability start time"
    )
    temp_to = models.TimeField(
        null=True, blank=True,
        help_text="Your temporary availability end time"
    )
    
    availability_type = models.CharField(
        max_length=20,
        choices=[
            ('weekday', 'Weekday'),
            ('weekend', 'Weekend'),
            ('temporary', 'Just for Today')
        ],
        default='weekday'
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
   
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Add this field to your Profile model
    is_profile_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def clean(self):
        if self.availability_type == 'weekday':
            from_time = self.weekday_from
            to_time = self.weekday_to
        elif self.availability_type == 'weekend':
            from_time = self.weekend_from
            to_time = self.weekend_to
        else:  # temporary
            from_time = self.temp_from
            to_time = self.temp_to

        if from_time and to_time:
            # Convert times to minutes since midnight for easier comparison
            from_minutes = from_time.hour * 60 + from_time.minute
            to_minutes = to_time.hour * 60 + to_time.minute
            
            # If end time is earlier than start time, assume it's the next day
            if to_minutes < from_minutes:
                # This is valid for night shifts
                return
                
            if from_minutes == to_minutes:
                raise ValidationError({
                    'to_time': 'Start and end times cannot be the same'
                })

    def is_currently_available(self):
        # Simplified to just return is_available field
        return self.is_available

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
    

class Project(models.Model):
    name = models.CharField(max_length=200)
    readme = models.TextField()
    deployed_url = models.URLField(blank=True, max_length=500)
    github_url = models.URLField(blank=True, null=True, max_length=500)
    client = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='projects')
    transaction_hash = models.CharField(max_length=66, blank=True, null=True)  # Ethereum tx hash is 66 chars
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('dev:project_detail', kwargs={'pk': self.pk})
    
    def clean(self):
        # More lenient URL validation
        if self.deployed_url:
            try:
                URLValidator(schemes=['http', 'https'])(self.deployed_url)
            except ValidationError:
                if not self.deployed_url.startswith(('http://', 'https://')):
                    self.deployed_url = 'https://' + self.deployed_url

        if self.github_url:
            try:
                URLValidator(schemes=['http', 'https'])(self.github_url)
            except ValidationError:
                if not self.github_url.startswith(('http://', 'https://')):
                    self.github_url = 'https://' + self.github_url

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Comment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.profile.user.username}'s profile"
    

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)
    
