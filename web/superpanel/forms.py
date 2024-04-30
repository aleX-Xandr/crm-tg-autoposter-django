from django import forms
from .models import UploadedFile

class FileUploadForm(forms.Form):

    remainingLinks = forms.CharField(max_length=1000)
    post_id = forms.CharField(max_length=100)
    
