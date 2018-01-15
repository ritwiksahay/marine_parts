  var responseHandler = function(status, response) {
        var $form = $('#payment-info-form');
        $('#someHiddenDiv').hide();
        if (status != 201) {
             if (response.error && status != 400) {
               var error = response["error"];
               var errormsg = error["messages"];
               var errorcode = JSON.stringify(errormsg[0].code, null, 4);
               var errorMessages = JSON.stringify(errormsg[0].description, null, 4);
               $('#payment-errors').html( 'Error Code:' + errorcode + ', Error Messages:'
                                + errorMessages);
            }
            if (status == 400 || status == 500) {
               $('#payment-errors').html('');
               var errormsg = response.Error.messages;
               var errorMessages = "";
               for(var i in errormsg){
                var ecode = errormsg[i].code;
                var eMessage = errormsg[i].description;
                errorMessages = errorMessages + 'Error Code:' + ecode + ', Error Messages:'
                                + eMessage;
                }

               $('#payment-errors').html( errorMessages);
            }
            $form.find('button').prop('disabled', false);
        } else {
            $('#payment-errors').html('');
            var result = response.token;
            $('#token_chk').attr('value', result.value);
            $('#payment-method').attr('value', 'payeezy');
            $('#cardholder_name').attr('value', result.cardholder_name);
            $('#card_type').attr('value', result.type);
            $('#exp_date').attr('value', result.exp_date);

            //$form.find('button').prop('disabled', false);
        }
    };

    jQuery(function($) {
        $('#payment-info-form').submit(function(e) {
            $('#response_msg').html('');
            $('#response_note').html('');
            $('#payment-errors').html('');
            var $form = $(this);
            $form.find('button').prop('disabled', true);
            var apiKey = 'y6pWAJNyJyjGv66IsVuWnklkKUPFbb0a';
            var js_security_key = 'js-6125e57ce5c46e10087a545b9e9d7354c23e1a1670d9e9c7';
            var auth = 'false';
            var ta_token = 'NOIW';
            var currency = 'USD';

            Payeezy.setApiKey(apiKey);
            Payeezy.setJs_Security_Key(js_security_key);
            Payeezy.setTa_token(ta_token);
            Payeezy.setAuth(auth);
            Payeezy.setcurrency(currency);
            Payeezy.createToken(responseHandler);
            $('#someHiddenDiv').show();
            return false;
        });
    });