from django import forms
from .models import WorkerProfile, Skill


class WorkerProfileForm(forms.ModelForm):
    class Meta:
        model = WorkerProfile
        fields = ['experience_years', 'daily_wage', 'availability']
        widgets = {
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'daily_wage': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'availability': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Skill name'}),
        }


class WorkerSkillForm(forms.Form):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
