# -*- coding: utf-8 -*-
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from oscar.apps.checkout import views
from oscar.apps.payment import forms, models

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController
import marine_parts.authorize.constants
#import imp


#CONSTANTS = imp.load_source('modulename', 'constants.py')


class PaymentDetailsView(views.PaymentDetailsView):
    """
    Vista de pago para el introducir, manejar y procesar los pagos por
    Authorize.net y Payeezy first data
    """

    def post(self, request, *args, **kwargs):
        # Override so we can validate the bankcard/billingaddress submission.
        # If it is valid, we render the preview screen with the forms hidden
        # within it.  When the preview is submitted, we pick up the 'action'
        # parameters and actually place the order.
        if request.POST.get('action', '') == 'place_order':
            return self.do_place_order(request)

        card_number = request.POST['card-number']
        cardCode = request.POST['cvv']

        print(card_number)
        # Validar la informacinhttps://github.com/django-oscar/django-oscar/blob/f34ee23785741d090e68c937e2a9fab2e
        if not (card_number and cardCode):
            return self.render_payment_details(request, cvv=cardCode)

        # Render preview with bankcard and billing address details hidden
        return self.render_preview(request,
                                   cvv=cardCode,
                                   cardNumber=card_number)

    def do_place_order(self, request):
        # Helper method to check that the hidden forms wasn't tinkered
        # with.
        card_number = request.POST["card-number"]
        cardCode = request.POST['cvv']

        if not (card_number and cardCode):
            messages.error(request, "Invalid submission")
            return HttpResponseRedirect(reverse('checkout:payment-details'))

        # Attempt to submit the order, passing the bankcard object so that it
        # gets passed back to the 'handle_payment' method below.
        submission = self.build_submission()
        submission['payment_kwargs']['card_number'] = card_number
        submission['payment_kwargs']['cvv'] = cardCode
        return self.submit(**submission)

    def handle_payment(self, order_number, total, **kwargs):
        """
        Make submission to PayPal
        """
        # Using authorization here (two-stage model).  You could use sale to
        # perform the auth and capture in one step.  The choice is dependent
        # on your business model.
        response = self.charge_credit_card(
            total.incl_tax
            , kwargs['card_number']
            , kwargs['cvv'])

        reference = "Transaction ID: " + response.transactionResponse.transId
        # Record payment source and event
        source_type, is_created = models.SourceType.objects.get_or_create(
            name='Authorize.net')
        source = source_type.sources.model(
            source_type=source_type,
            amount_allocated=total.incl_tax,
            currency=total.currency,
            reference=reference)

        self.add_payment_source(source)

        # Note that payment events don’t distinguish between different sources.
        self.add_payment_event('Successfully charged', total.incl_tax)

    def charge_credit_card(self, amount, card_number, cardCode):
        """
        Charge a credit card
        """

        # BORRAR para consultar con estas constanes aparte
        apiLoginId = "6X5kyB5yF"
        transactionKey = "8hr8HwR2TSU83H4D"
        transactionId = "2245440957"
        # Create a merchantAuthenticationType object with authentication details
        # retrieved from the constants file
        merchantAuth = apicontractsv1.merchantAuthenticationType()
        merchantAuth.name = apiLoginId
        merchantAuth.transactionKey = transactionKey

        # Create the payment data for a credit card
        creditCard = apicontractsv1.creditCardType()
        creditCard.cardNumber = card_number
        creditCard.expirationDate = "2020-12"
        creditCard.cardCode = cardCode

        # Add the payment data to a paymentType object
        payment = apicontractsv1.paymentType()
        payment.creditCard = creditCard

        # Create order information
        order = apicontractsv1.orderType()
        order.invoiceNumber = "10101"
        order.description = "Golf Shirts"

        # Set the customer's Bill To address
        customerAddress = apicontractsv1.customerAddressType()
        customerAddress.firstName = "Ellen"
        customerAddress.lastName = "Johnson"
        customerAddress.company = "Souveniropolis"
        customerAddress.address = "14 Main Street"
        customerAddress.city = "Pecan Springs"
        customerAddress.state = "TX"
        customerAddress.zip = "44628"
        customerAddress.country = "USA"

        # Set the customer's identifying information
        customerData = apicontractsv1.customerDataType()
        customerData.type = "individual"
        customerData.id = "99999456654"
        customerData.email = "EllenJohnson@example.com"

        # Add values for transaction settings
        duplicateWindowSetting = apicontractsv1.settingType()
        duplicateWindowSetting.settingName = "duplicateWindow"
        duplicateWindowSetting.settingValue = "600"
        settings = apicontractsv1.ArrayOfSetting()
        settings.setting.append(duplicateWindowSetting)

        # setup individual line items
        line_item_1 = apicontractsv1.lineItemType()
        line_item_1.itemId = "12345"
        line_item_1.name = "first"
        line_item_1.description = "Here's the first line item"
        line_item_1.quantity = "2"
        line_item_1.unitPrice = "12.95"
        line_item_2 = apicontractsv1.lineItemType()
        line_item_2.itemId = "67890"
        line_item_2.name = "second"
        line_item_2.description = "Here's the second line item"
        line_item_2.quantity = "3"
        line_item_2.unitPrice = "7.95"

        # build the array of line items
        line_items = apicontractsv1.ArrayOfLineItem()
        line_items.lineItem.append(line_item_1)
        line_items.lineItem.append(line_item_2)

        # Create a transactionRequestType object and add the previous objects to it.
        transactionrequest = apicontractsv1.transactionRequestType()
        transactionrequest.transactionType = "authCaptureTransaction"
        transactionrequest.amount = amount
        transactionrequest.payment = payment
        transactionrequest.order = order
        transactionrequest.billTo = customerAddress
        transactionrequest.customer = customerData
        transactionrequest.transactionSettings = settings
        transactionrequest.lineItems = line_items

        # Assemble the complete transaction request
        createtransactionrequest = apicontractsv1.createTransactionRequest()
        createtransactionrequest.merchantAuthentication = merchantAuth
        createtransactionrequest.refId = "MerchantID-0001"
        createtransactionrequest.transactionRequest = transactionrequest
        # Create the controller
        createtransactioncontroller = createTransactionController(
            createtransactionrequest)
        createtransactioncontroller.execute()

        response = createtransactioncontroller.getresponse()

        if response is not None:
            # Check to see if the API request was successfully received and acted upon
            if response.messages.resultCode == "Ok":
                # Since the API request was successful, look for a transaction response
                # and parse it to display the results of authorizing the card
                if hasattr(response.transactionResponse, 'messages') is True:
                    print(
                        'Successfully created transaction with Transaction ID: %s'
                        % response.transactionResponse.transId)
                    print('Transaction Response Code: %s' %
                          response.transactionResponse.responseCode)
                    print('Message Code: %s' %
                          response.transactionResponse.messages.message[0].code)
                    print('Description: %s' % response.transactionResponse.
                          messages.message[0].description)
                else:
                    print('Failed Transaction.')
                    if hasattr(response.transactionResponse, 'errors') is True:
                        print('Error Code:  %s' % str(response.transactionResponse.
                                                      errors.error[0].errorCode))
                        print(
                            'Error message: %s' %
                            response.transactionResponse.errors.error[0].errorText)
            # Or, print errors if the API request wasn't successful
            else:
                print('Failed Transaction.')
                if hasattr(response, 'transactionResponse') is True and hasattr(
                        response.transactionResponse, 'errors') is True:
                    print('Error Code: %s' % str(
                        response.transactionResponse.errors.error[0].errorCode))
                    print('Error message: %s' %
                          response.transactionResponse.errors.error[0].errorText)
                else:
                    print('Error Code: %s' %
                          response.messages.message[0]['code'].text)
                    print('Error message: %s' %
                          response.messages.message[0]['text'].text)
        else:
            print('Null Response.')

        return response
