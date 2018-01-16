from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from oscar.apps.checkout import views
from oscar.apps.payment import forms, models, exceptions

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController

from marine_parts.payment_mods.libPayeezy import setup_params_request, execPaymentPayeezySandbox, execPaymentPayeezyLive

class PaymentDetailsView(views.PaymentDetailsView):
    """
    Vista de pago para introducir, manejar y procesar los pagos por
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
            token_chk = request.POST['token_chk']
            card_type = request.POST['card_type']
            cardholder_name = request.POST['cardholder_name']
            exp_date = request.POST['exp_date']
            if token_chk and card_type and cardholder_name and exp_date:
                # Render preview with bankcard and billing address details hidden

                return self.render_preview(request, token_chk=token_chk, card_type=card_type
                           , cardholder_name=cardholder_name, exp_date=exp_date, payment_method=payment_m)
            else:
                return self.render_payment_details(request)
        else:
            token = request.POST['dataValue']
            descriptor = request.POST['dataDescriptor']
            if token and descriptor:
                return self.render_preview(request, token=token, payment_method=payment_m, descriptor=descriptor)
            else:
                return self.render_payment_details(request)


    def do_place_order(self, request):
        # Helper method to check that the hidden forms wasn't tinkered
        # with.
        submission = self.build_submission()
        submission['payment_kwargs']['payment_method'] = request.POST['payment-method']
        if request.POST['payment-method'] == 'payeezy':
            token = request.POST['token_chk']
            card_type = request.POST['card_type']
            cardholder_name = request.POST['cardholder_name']
            exp_date = request.POST['exp_date']
            submission['payment_kwargs']['token_chk'] = token
            submission['payment_kwargs']['cardholder_name'] = cardholder_name
            submission['payment_kwargs']['card_type'] = card_type
            submission['payment_kwargs']['exp_date'] = exp_date
            if not (token and card_type and cardholder_name and exp_date):
                messages.error(request, "Invalid submission")
                return HttpResponseRedirect(reverse('checkout:payment-details'))
        else:
            token = request.POST['dataValue']
            descriptor = request.POST['dataDescriptor']
            submission['payment_kwargs']['token_chk'] = token
            submission['payment_kwargs']['descriptor'] = descriptor
            if not (token and descriptor):
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
        import pdb; pdb.set_trace()
        if kwargs['payment_method'] == 'payeezy':
            self.execPayeezy(order_number, total, kwargs)
        else:
            #
            # Authorize.net payment
            #
            self.create_an_accept_payment_transaction(order_number
                                                      , kwargs['token_chk'], kwargs['descriptor'], total )

    def execPayeezy(self, order_number, total, tk_card):

        headers, payload = setup_params_request(str(total.incl_tax), tk_card['card_type']
                                                , tk_card['token_chk']
                                                , tk_card['cardholder_name']
                                                , tk_card['exp_date'])

        # When it's deployed, comment this line and uncoment the next line
        isSucess, reference = execPaymentPayeezySandbox(order_number, headers, payload)
        #isSucess, reference = execPaymentPayeezyLive(order_number, headers, payload)

        if isSucess:
            # Record payment source and event
            self.recordPayment('Payeezy', total, reference)
        else:
            raise exceptions.UnableToTakePayment


    def recordPayment(self, name, total, reference):
        source_type, is_created = models.SourceType.objects.get_or_create(name=name)
        source = source_type.sources.model(
            source_type=source_type,
            amount_allocated=total.incl_tax,
            currency=total.currency,
            reference=reference)
        self.add_payment_source(source)
        # Note that payment events don't distinguish between different sources.
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