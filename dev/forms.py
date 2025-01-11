from django import forms
from .models import Profile, Skill

class ProfileForm(forms.ModelForm):
    display_name = forms.CharField(
        max_length=50,
        required=True,
        help_text="Name that will be shown to others"
    )
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    available_from = forms.TimeField(
        required=True,
        widget=forms.TimeInput(
            attrs={'type': 'time'},
            format='%H:%M'
        ),
        help_text="Your availability start time (in your timezone)"
    )
    available_to = forms.TimeField(
        required=True,
        widget=forms.TimeInput(
            attrs={'type': 'time'},
            format='%H:%M'
        ),
        help_text="Your availability end time (in your timezone)"
    )

    class Meta:
        model = Profile
        fields = [
            'display_name', 'profile_picture', 'bio', 'title', 
            'years_of_experience', 'hourly_rate', 'crypto_wallet_address',
            'skills', 'github_url', 'linkedin_url', 'portfolio_url',
            'is_available', 'available_from', 'available_to', 'timezone',
            'preferred_contact_method', 'min_project_duration', 
            'preferred_project_size', 'certifications', 'education'
        ]

    def clean(self):
        cleaned_data = super().clean()
        available_from = cleaned_data.get('available_from')
        available_to = cleaned_data.get('available_to')

        if available_from and available_to:
            if available_from >= available_to:
                raise forms.ValidationError({
                    'available_to': 'End time must be after start time'
                })
        return cleaned_data 