from django import forms
from django.forms.widgets import FileInput
from .models import HouseRequirement, MediaUpload


class MultipleFileInput(FileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['multiple'] = True
        super().__init__(attrs)


class HouseRequirementForm(forms.ModelForm):
    class Meta:
        model = HouseRequirement
        fields = ['plot_size', 'budget', 'floors', 'city']
        widgets = {
            'plot_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1000 sq ft'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'floors': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city name'}),
        }


class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = MediaUpload
        fields = ['media_type', 'file_path']
        widgets = {
            'media_type': forms.Select(attrs={'class': 'form-control'}),
            'file_path': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,video/*'}),
        }


class MultipleMediaUploadForm(forms.Form):
    files = forms.FileField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,video/*'
        }),
        required=False,
        help_text="Upload multiple files (images, videos)"
    )
