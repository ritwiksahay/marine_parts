from django import forms
from pyexcel_xlsx import get_data

class UploadFileForm(forms.Form):
    file = forms.FileField(required=True, max_length=3000)
