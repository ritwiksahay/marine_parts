import unittest
from libPayeezy import setup_params_request, execPaymentPayeezy
import constants

#Integration tests
class LibPayeezyTest(unittest.TestCase):
    def setUp(self):
        self.test_card = {
            "type": "visa",
            "cardholder_name": "JohnSmith",
            "card_number": "2537446225198291",
            "exp_date": "1030",
            "cvv": "123"
        }

    def test_execPaymentPayeezyValid_ReturnsTrue(self):
        headers, payload = setup_params_request('200', self.test_card['type']
             , self.test_card['card_number']
             , self.test_card["cardholder_name"]
             , self.test_card['exp_date'])

        isSucess, _ = execPaymentPayeezy(constants.url_payeezy_sandbox, 1, payload, headers)

        self.assertTrue(isSucess)

    def test_execPaymentPayeezyWithoutCardNumber_ReturnsFalse(self):
        headers, payload = setup_params_request('200', self.test_card['type']
             , ''
             , self.test_card["cardholder_name"]
             , self.test_card['exp_date'])

        isSucess, _ = execPaymentPayeezy(constants.url_payeezy_sandbox, 1, headers, payload)

        self.assertFalse(isSucess)

if __name__ == '__main__':
    unittest.main()




