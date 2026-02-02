from django import forms
from .models import ThekedarProfile, Project
from workers.models import Skill


class ThekedarProfileForm(forms.ModelForm):
    class Meta:
        model = ThekedarProfile
        fields = ['experience_years', 'company_name']
        widgets = {
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'budget', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Project description'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class JobPostForm(forms.Form):
    required_skill = forms.ModelChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select a skill..."
    )
    duration_days = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )
    wage_offer = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'})
    )
