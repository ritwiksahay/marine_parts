from datetime import date
from django import forms
from django.utils.translation import ugettext_lazy as _


class PayeezyForm(forms.Form):

    card_types = (
        (None, _('--Select Card Type--')),
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('american', 'American Express'),
        ('discover', 'Discover'),
    )

    months = (
        ('01', _('January (01)')),
        ('02', _('February (02)')),
        ('03', _('March (03)')),
        ('04', _('April (04)')),
        ('05', _('May (05)')),
        ('06', _('June (06)')),
        ('07', _('July (07)')),
        ('08', _('August (08)')),
        ('09', _('September (09)')),
        ('10', _('October (10)')),
        ('11', _('November (11)')),
        ('12', _('December (12)')),
    )

    year = date.today().year
    years = (
        (str(item)[2:], str(item)) for item in tuple(range(year, year + 10))
    )

    card_type = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'payeezy-data': 'card_type',
            }
        ),
        choices=card_types,
    )
    cardholder = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'payeezy-data': 'cardholder_name',
            }
        ),
        help_text=_('Card Name')
    )
    card_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'payeezy-data': 'cc_number',
            }
        ),
        help_text=_('Card Number')
    )
    ccv_code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'payeezy-data': 'cvv_code',
            }
        ),
        help_text=_('Card CCV Code')
    )
    exp_month = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'payeezy-data': 'exp_month',
            }
        ),
        choices=months
    )
    exp_year = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'payeezy-data': 'exp_year',
            }
        ),
        choices=years
    )
