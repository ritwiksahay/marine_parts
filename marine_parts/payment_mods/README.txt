########################################################################################################################
Autor: Daniel Leones
Fecha: 15/01/2018
Descripción: Libreria de pago para Payeezy y Authorize.net. Para la fecha (15/01/2018) sólo cuenta con Payeezy.
El modulo 'constant' se utiliza para almacenar las credenciales de uso proveniente de las pasarelas.
Dependencias: requests==2.18.4, módulo constant
########################################################################################################################


########################################################################################################################
    INFORMACIÓN
########################################################################################################################

La integración de Payeezy se realiza con Payeezy.js (Más información: https://github.com/payeezy/payeezy_js)
y la libreria desarrollada. La primera funciona solicitando un token para asegurar el número de tarjeta de credito y
la segunda se basa en Token Based Payments (Más información:
https://developer.payeezy.com/payeezy-api/apis/post/transactions-4), la cual emplea el token, producto de Payezzy.js,
para realizar los pagos. Esta cadena de pago se ejecuta en el checkout del portal.

########################################################################################################################
    COMO USAR
########################################################################################################################

Para habilitar las pasarelas en modo producción:
    - Registrar al mercader en el portal de Payeezy. Obtener tu transarmor y su ta_token. Se edita el script js
     paymentHandler.js. (Más info: https://github.com/payeezy/payeezy_js/raw/master/guide/payeezy_js07012015.pdf)
    - Payeezy: usar la función execPaymentPayeezyLive con los datos apropiados.


Para usar la pasarela se utiliza el siguiente pesudocódigo a modo de ilustración:
     def ejecPayeezy(order_number, amount, card_type, token_chk, cardholder_name, exp_date):
        # El parametro amount es string
        headers, payload = setup_params_request(amount, card_type, token_chk, cardholder_name, exp_date)

        # Usar Sandbox o Live
        isSucess, reference = execPaymentPayeezySandbox(order_number, headers, payload)
        #isSucess, reference = execPaymentPayeezyLive(order_number, headers, payload)

        if isSucess:
            # Record payment source and event
        else:
            # Reportar error


########################################################################################################################

gen_hmac, get_nonce, get_timestamp y setup_params_request son funciones auxiliares para construir el request dirigido a la
pasarela de pago (Más información: https://developer.payeezy.com/payeezy-api/apis/post/transactions-4)


Notas:

    - Es opcional el uso de 'order_number'.

########################################################################################################################
    TESTS
########################################################################################################################

En tests.py se realizan pruebas de integración de la libreria

# Agregar pruebas para los siguientes casos
Tarjetas de diferentes tipos (Tarjetas de tipos válidos)
Tarjetas con números distintos a los indicados