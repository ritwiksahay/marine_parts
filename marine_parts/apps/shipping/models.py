from oscar.apps.shipping.models import *  # noqa isort:skip
from oscar.apps.shipping.methods import Free
from django.utils.translation import ugettext_lazy as _


class ReqAddrShipping(Free):
    """
    This shipping method specifies that shipping is free.
    """
    code = 'need-addr-shipping'
    name = _('Require address shipping')
