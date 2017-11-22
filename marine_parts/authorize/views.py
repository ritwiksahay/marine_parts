from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from oscar.apps.checkout import views
from oscar.apps.payment import forms, models, exceptions
import time

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController
import requests
from marine_parts.authorize import constants


class PaymentDetailsView(views.PaymentDetailsView):
    """
    Vista de pago para el introducir, manejar y procesar los pagos por
    Authorize.net y Payeezy first data
    """

    def post(self, request, *args, **kwargs):
        # Override so we can validate the bankcard submission.
        # If it is valid, we render the preview screen with the forms hidden
        # within it.  When the preview is submitted, we pick up the 'action'
        # parameters and actually place the order.
        if request.POST.get('action', '') == 'place_order':
            return self.do_place_order(request)

        payment_m = request.POST['payment-method']
        if  payment_m == 'payeezy':
            token = request.POST['token_chk']
            card_type = request.POST['card_type']
            cardholder_name = request.POST['cardholder_name']
            exp_date = request.POST['exp_date']
            if token and card_type and cardholder_name and exp_date:
                # Render preview with bankcard and billing address details hidden
                return self.render_preview(request, token=token, card_type=card_type
                                           , cardholder_name=cardholder_name, exp_date=exp_date, payment_method=payment_m)
            else:
                return self.render_payment_details(requests)
        else:
            token = request.POST['dataValue']
            descriptor = request.POST['dataDescriptor']
            if token and descriptor:
                return self.render_preview(request, token=token, payment_method=payment_m, descriptor=descriptor )
            else:
                return self.render_payment_details(requests)


    def do_place_order(self, request):
        # Helper method to check that the hidden forms wasn't tinkered
        # with.
        submission = self.build_submission()
        submission['payment_kwargs']['payment-method'] = request.POST['payment-method']
        if  request.POST['payment-method'] == 'payeezy':
            token = request.POST['token_chk']
            card_type = request.POST['card_type']
            cardholder_name = request.POST['cardholder_name']
            exp_date = request.POST['exp_date']
            if token and card_type and cardholder_name and exp_date:
                submission['payment_kwargs']['token_chk'] = token
                submission['payment_kwargs']['cardholder_name'] = cardholder_name
                submission['payment_kwargs']['card_type'] = card_type
                submission['payment_kwargs']['exp_date'] = exp_date
            else:
                messages.error(request, "Invalid submission")
                return HttpResponseRedirect(reverse('checkout:payment-details'))
        else:
            token = request.POST['dataValue']
            descriptor = request.POST['dataDescriptor']
            if token and descriptor:
                submission['payment_kwargs']['token_chk'] = token
                submission['payment_kwargs']['descriptor'] = descriptor
            else:
                messages.error(request, "Invalid submission")
                return HttpResponseRedirect(reverse('checkout:payment-details'))

        # Attempt to submit the order, passing the bankcard object so that it
        # gets passed back to the 'handle_payment' method below.

        return self.submit(**submission)

    def handle_payment(self, order_number, total, **kwargs):
        """
        Make submission to Authorize.net and Payeezy
        """
        #
        # Payeezy payment
        #
        if kwargs['payment-method'] == 'payeezy':
            constants.payload['amount'] = str(total.incl_tax)
            constants.payload['token']['token_data']['type'] = kwargs['card_type']
            constants.payload['token']['token_data']['value'] = kwargs['token_chk']
            constants.payload['token']['token_data']['cardholder_name'] = kwargs['cardholder_name']
            constants.payload['token']['token_data']['exp_date'] = kwargs['exp_date']
            self.execPaymentPayeezy(order_number, total)

        else:
            #
            # Authorize.net payment
            #
            self.create_an_accept_payment_transaction(order_number
                  , kwargs['token_chk'], kwargs['descriptor'], total )

    def execPaymentPayeezy(self, order_number, total, payload):
        # Charge the token requested
        response = requests.post(constants.url_payeezy_sandbox, json=constants.payload, headers=constants.headers)
        # Check errors
        #print('Response: ' + str(response.status_code))
        response_json = response.json()
        if response.status_code >= 400:
            # print("Transaction status: " + response_json['transaction_status'])
            #print(response_json)
            #for x in response_json['Error']['messages']:
                #print(x['code'] + " " + x['description'])
            raise exceptions.UnableToTakePayment
        else:
            # Notify payment event if there is success
            reference = "Transaction ID: %s\nBank response code: %s\n, Bank message: %s\n" \
                        % (
                        response_json['transaction_id'], response_json['bank_resp_code'], response_json['bank_message'])

            # Record payment source and event
            self.recordPayment('Payeezy', total, reference)

    def recordPayment(self, name, total, reference):
        source_type, is_created = models.SourceType.objects.get_or_create(name=name)
        source = source_type.sources.model(
            source_type=source_type,
            amount_allocated=total.incl_tax,
            currency=total.currency,
            reference=reference)
        self.add_payment_source(source)
        # Note that payment events don’t distinguish between different sources.
        self.add_payment_event(name, total.incl_tax, reference)


    def create_an_accept_payment_transaction(self, order_number, dataValue, dataDescriptor, total):
        # Create a merchantAuthenticationType object with authentication details
        # retrieved from the constants file
        merchantAuth = apicontractsv1.merchantAuthenticationType()
        merchantAuth.name = constants.apiLoginId
        merchantAuth.transactionKey = constants.transactionKey

        # Create the payment object for a payment nonce
        opaqueData = apicontractsv1.opaqueDataType()
        opaqueData.dataDescriptor = dataDescriptor
        opaqueData.dataValue = dataValue

        # Add the payment data to a paymentType object
        paymentOne = apicontractsv1.paymentType()
        paymentOne.opaqueData = opaqueData

        # Create order information
        #order = apicontractsv1.orderType()
        #order.invoiceNumber = "10101"
        #order.description = "Golf Shirts"

        # Add values for transaction settings
        duplicateWindowSetting = apicontractsv1.settingType()
        duplicateWindowSetting.settingName = "duplicateWindow"
        duplicateWindowSetting.settingValue = "600"
        settings = apicontractsv1.ArrayOfSetting()
        settings.setting.append(duplicateWindowSetting)

        # Create a transactionRequestType object and add the previous objects to it
        transactionrequest = apicontractsv1.transactionRequestType()
        transactionrequest.transactionType = "authCaptureTransaction"
        transactionrequest.amount = total.incl_tax
        #transactionrequest.order = order
        transactionrequest.payment = paymentOne

        # Assemble the complete transaction request
        createtransactionrequest = apicontractsv1.createTransactionRequest()
        createtransactionrequest.merchantAuthentication = merchantAuth
        # Set the transaction's refId
        createtransactionrequest.refId = str(order_number)
        createtransactionrequest.transactionRequest = transactionrequest

        # Create the controller and get response
        createtransactioncontroller = createTransactionController(createtransactionrequest)
        createtransactioncontroller.execute()

        response = createtransactioncontroller.getresponse()

        if response is not None:
            # Check to see if the API request was successfully received and acted upon
            if response.messages.resultCode == "Ok":
                # Since the API request was successful, look for a transaction response
                # and parse it to display the results of authorizing the card
                if hasattr(response.transactionResponse, 'messages'):
                    reference = "Transaction ID: %s\nAuth Code: %s\nTransaction Response Code: %s" \
                                % (response.transactionResponse.transId, response.transactionResponse.authCode,
                                   response.transactionResponse.responseCode)
                    # Record payment source and event
                    self.recordPayment('Authorize.net', total, reference)
                else:
                    # print('Failed Transaction.')
                    # if hasattr(response.transactionResponse, 'errors') == True:
                    #     print('Error Code:  %s' % str(response.transactionResponse.errors.error[0].errorCode))
                    #     print('Error message: %s' % response.transactionResponse.errors.error[0].errorText)
                    raise exceptions.UnableToTakePayment
            else:
                # print('Failed Transaction.')
                # if hasattr(response, 'transactionResponse') == True and hasattr(response.transactionResponse,
                #                                                                 'errors') == True:
                #     print('Error Code: %s' % str(response.transactionResponse.errors.error[0].errorCode))
                #     print('Error message: %s' % response.transactionResponse.errors.error[0].errorText)
                # else:
                #     print('Error Code: %s' % response.messages.message[0]['code'].text)
                #     print('Error message: %s' % response.messages.message[0]['text'].text)
                raise exceptions.PaymentError
        else:
            raise exceptions.PaymentError