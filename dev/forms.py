from django import forms
from .models import Profile, Skill, Project
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'readme', 'deployed_url', 'github_url', 'client']
        widgets = {
            'readme': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_deployed_url(self):
        url = self.cleaned_data.get('deployed_url')
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            try:
                URLValidator(schemes=['http', 'https'])(url)
            except ValidationError:
                raise ValidationError('Enter a valid URL.')
        return url

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        try:
            URLValidator(schemes=['http', 'https'])(url)
        except ValidationError:
            raise ValidationError('Enter a valid URL.')
        return url

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
    weekday_from = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={'type': 'time', 'class': 'time-input weekday-time'},
            format='%H:%M'
        )
    )
    weekday_to = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={'type': 'time', 'class': 'time-input weekday-time'},
            format='%H:%M'
        )
    )
    weekend_from = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={'type': 'time', 'class': 'time-input weekend-time'},
            format='%H:%M'
        )
    )
    weekend_to = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={'type': 'time', 'class': 'time-input weekend-time'},
            format='%H:%M'
        )
    )
    temp_from = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={'type': 'time', 'class': 'time-input temp-time'},
            format='%H:%M'
        )
    )
    temp_to = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={'type': 'time', 'class': 'time-input temp-time'},
            format='%H:%M'
        )
    )
    availability_type = forms.ChoiceField(
        choices=[
            ('weekday', 'Weekday'),
            ('weekend', 'Weekend'),
            ('temporary', 'Just for Today')
        ],
        widget=forms.RadioSelect,
        initial='weekday'
    )
    manual_availability_duration = forms.IntegerField(
        required=False,
        min_value=1,
        help_text="Number of hours to remain available",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = [
            'display_name', 'profile_picture', 'bio', 'title', 
            'years_of_experience', 'hourly_rate', 'crypto_wallet_address',
            'skills', 'github_url', 'linkedin_url', 'portfolio_url',
            'is_available', 'timezone', 'preferred_contact_method', 
            'min_project_duration', 'preferred_project_size',
            'weekday_from', 'weekday_to',
            'weekend_from', 'weekend_to',
            'temp_from', 'temp_to',
            'availability_type',
            'manual_availability',
            'manual_availability_end'
        ]

    def clean(self):
        cleaned_data = super().clean()
        availability_type = cleaned_data.get('availability_type')
        manual_availability = cleaned_data.get('manual_availability')
        duration = cleaned_data.get('manual_availability_duration')

        if manual_availability and duration:
            from datetime import datetime, timedelta
            import pytz
            cleaned_data['manual_availability_end'] = datetime.now(pytz.UTC) + timedelta(hours=duration)

        if availability_type == 'weekday':
            from_time = cleaned_data.get('weekday_from')
            to_time = cleaned_data.get('weekday_to')
        elif availability_type == 'weekend':
            from_time = cleaned_data.get('weekend_from')
            to_time = cleaned_data.get('weekend_to')
        else:  # temporary
            from_time = cleaned_data.get('temp_from')
            to_time = cleaned_data.get('temp_to')

        if from_time and to_time:
            # Convert times to minutes since midnight for easier comparison
            from_minutes = from_time.hour * 60 + from_time.minute
            to_minutes = to_time.hour * 60 + to_time.minute
            
            # If end time is earlier than start time, assume it's the next day
            if to_minutes < from_minutes:
                # This is valid for night shifts
                return cleaned_data
                
            if from_minutes == to_minutes:
                raise forms.ValidationError('Start and end times cannot be the same')
                
        return cleaned_data 