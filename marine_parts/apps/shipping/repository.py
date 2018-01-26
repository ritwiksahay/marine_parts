from decimal import Decimal as D
from oscar.apps.shipping.methods import Free, FixedPrice, NoShippingRequired
from oscar.apps.shipping.repository import Repository as CoreRepository
from oscar.apps.shipping import methods, models
from marine_parts.apps.shipping.models import ReqAddrShipping
from oscar.apps.shipping.models import WeightBased, OrderAndItemCharges
from django.utils.translation import ugettext_lazy as _


class Repository(CoreRepository):
    methods = []  # init shipping method to default hand delivery

    def get_available_shipping_methods(
            self, basket, user=None, shipping_addr=None,
            request=None, **kwargs):
        # National shipping
        methods = []
        #import pdb; pdb.set_trace()
        if shipping_addr:
            if shipping_addr.country.code == 'US':
                methods = list(WeightBased.objects.all().filter(countries='US'))
            else:
                methods = list(WeightBased.objects.all().filter(countries=shipping_addr.country.code))
        else:
            methods = [ReqAddrShipping()]

        return methods