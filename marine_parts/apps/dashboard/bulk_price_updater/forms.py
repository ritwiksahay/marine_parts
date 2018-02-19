import os
from django import forms
from oscar.apps.partner.models import Partner
from django.utils.translation import ugettext_lazy as _


class ExtFileField(forms.FileField):
    """
    Same as forms.FileField, but you can specify a file extension whitelist.

    >>> from django.core.files.uploadedfile import SimpleUploadedFile
    >>>
    >>> t = ExtFileField(ext_whitelist=(".pdf", ".txt"))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.pdf', 'Some File Content'))
    >>> t.clean(SimpleUploadedFile('filename.txt', 'Some File Content'))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.exe', 'Some File Content'))
    Traceback (most recent call last):
    ...
    ValidationError: [u'Not allowed filetype!']
    """

    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]
        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ExtFileField, self).clean(*args, **kwargs)
        filename = data.name
        ext = os.path.splitext(filename)[1]
        ext = ext.lower()
        if ext not in self.ext_whitelist:
            raise forms.ValidationError("Not allowed filetype!")


class UploadFileForm(forms.Form):
    file = ExtFileField(
        label=_('Select file'),
        help_text=_("File extension must be .xls, .xlsx or .csv"),
        required=True,
        max_length=3000,
        ext_whitelist= ('.csv, .xls, .xlsx'))

    partner = forms.ModelChoiceField(
        label=_("Update"),
        empty_label=_("-- Choose partner --"),
        queryset=Partner.objects.all(),
        required=True)

    percent = forms.DecimalField(decimal_places=2, initial=0.00,
         help_text=_("Use positive value to increase or negative one to decrease"))


