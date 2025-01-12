from django.db import models
from django.contrib.auth.models import User
from dev.models import Profile as DevProfile
from django.utils import timezone
from django.db.models import JSONField
from my_dapp.backend_service import release_funds

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    crypto_wallet_address = models.CharField(max_length=42, blank=True, null=True)
    
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
    requester_type = models.CharField(max_length=20, choices=REQUESTER_CHOICES, default='developer')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # If request is approved and status is completed, trigger payment release
        if self.is_approved and self.requested_status == 'completed':
            try:
                print("\n=== Payment Release Process Start ===")
                
                # Get addresses first and validate
                sender = self.project.customer.user.customerprofile.crypto_wallet_address
                recipient = self.project.assigned_developer.crypto_wallet_address
                
                if not sender:
                    print("Error: Customer wallet address is not set!")
                    return
                    
                if not recipient:
                    print("Error: Developer wallet address is not set!")
                    return
                    
                print(f"Sender Address: {sender}")
                print(f"Recipient Address: {recipient}")
                
                # Setup Web3
                w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
                if not w3.is_connected():
                    print("Error: Cannot connect to Web3!")
                    return
                print(f"Web3 Connected: {w3.is_connected()}")
                
                # Validate addresses
                if not w3.is_address(sender):
                    print(f"Error: Invalid sender address format: {sender}")
                    return
                    
                if not w3.is_address(recipient):
                    print(f"Error: Invalid recipient address format: {recipient}")
                    return
                
                # Load contract details
                print("Loading contract details...")
                with open('my_dapp/contract_abi.json', 'r') as f:
                    contract_abi = json.load(f)
                with open('my_dapp/contract_address.txt', 'r') as f:
                    contract_address = f.read().strip()
                print(f"Contract Address: {contract_address}")
                
                amount = self.project.budget
                print(f"Amount: {amount}")
                
                # Import and call release_funds
                from my_dapp.backend_service import release_funds
                print("Calling release_funds...")
                
                result = release_funds(
                    contract_address=contract_address,
                    sender=sender,
                    recipient=recipient,
                    amount=amount
                )
                
                print(f"Payment Release Result: {result}")
                print("=== Payment Release Process Complete ===\n")
                
            except Exception as e:
                print(f"Error releasing payment: {str(e)}")
                print(f"Error type: {type(e)}")
                print("=== Payment Release Process Failed ===\n")
