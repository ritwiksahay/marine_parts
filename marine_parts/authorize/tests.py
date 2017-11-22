from marine_parts.authorize import views
from django.test import RequestFactory
from django.test import Client
from django.test import TestCase
from marine_parts.users.models import User
from oscar.test import factories
from oscar.test.basket import add_product
from decimal import Decimal as D

from oscar.apps.basket import middleware

from django.contrib.sessions.middleware import SessionMiddleware
from oscar.test.factories import BasketFactory
#from oscar.test.utils import RequestFactory

class PaymentDetailsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url_payment_details = '/checkout/payment-details/'
        # Fixtures
        self.user = User.objects.create_user(email='dleones@ubicutus.com', password='1234qwer')
        # Login to access to payment views)
        self.client.login(email='dleones@ubicutus.com', password='1234qwer')

        self.data_payeezy = {
            'payment-method' : 'payeezy',
            # Token got by Payeezy JS Library
            'token_chk' : '2537446225198291',
            'card_type' : 'visa',
            'cardholder_name' : 'xzy',
            'exp_date' : '1223'
        }

        self.data_authorizenet = {
            'payment-method': 'payeezy',
            'dataValue': 'COMMON.ACCEPT.INAPP.PAYMENT',
            'dataDescriptor': 'eyJjb2RlIjoiNTBfMl8wNjAwMDUzNDA5QUVCNzA4QzVBOTE5QjMzMTVFMDk4RDBGQzI5NkYyOEU2OTUwRjJBM0Q3RDBBMjAxODY2MkJGQjVDRjU4ODBFQTBDNDkxMzU3MUY0Q0M0MEJGQ0MxOUMzRkUwMENFIiwidG9rZW4iOiI5NTExMzY1NzM2ODQxMDI1NDAzNTAyIiwidiI6IjEuMSJ9',
        }

        #self.middleware =  middleware.BasketMiddleware()

    def test_PaymentDetailView_VerifyGetClassView(self):
        response = self.client.get('/checkout/payment-details/')
        self.assertEqual(response.resolver_match.func.__name__,views.PaymentDetailsView.as_view().__name__)

    def test_PaymentDetailView_postValid_authorize(self):

        response = self.client.post(self.url_payment_details, self.data_authorizenet, secure=True, follow=True)
        # Create a dummy basket for session
        #basket = factories.create_basket(empty=True)
        #add_product(basket, D('12.00'))
        #self.product = factories.create_product(num_in_stock=10)

        # Agregar session middleware
        #request = RequestFactory().post('/checkout/payment-details/', data, secure=True)
        #request.user = self.user
        #self.middleware.process_request(request)
        #request.basket = basket
        #request.session = {}
        #response = views.PaymentDetailsView.as_view()(request)
        print(response.redirect_chain)
        self.assertEqual(response.status_code, 200)







