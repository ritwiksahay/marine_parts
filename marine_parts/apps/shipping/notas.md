# Shipping

Este documento resume las decisiones de diseño tomadas para implementar este módulo.

## Shipping tab

En `settings.py`, se habilita esta pestaña con el siguiente código:

```python
OSCAR_DASHBOARD_NAVIGATION += [
    {
        'label': 'Shipping',
        'icon': 'icon-map-marker',
        'children' : [
            {
                'label': 'Shipping Methods',
                'url_name': 'dashboard:shipping-method-list'
            }
        ]
    }
]
```


Los métodos, para que sean aplicables al cliente del portal, requieren un ámbito de paises.

A partir de allí se define los shipping methods que utilizará el portal.

## Shipping Methods
En la carpeta `fixtures` yacen los métodos para ser usados en producción. Estos se crearon a partir de los
`WeightBased` para el manejo envios nacionales e internacionles junto con `WeightBand` para el manejo de los casos
especiales.

Para activar el reconocimiento de peso y el proceso de cobro, en los `ProductClass` debe estar definido
un `ProductAttribute` con `code = weight` de tipo `Float`. En caso que no exista un atributo `weight`, se considera
`weight = 0.0` y aplica una tarifa base (una `WeightBand` inferior).


## Shipping Address

Se creó un método ficticio denominado `ReqAddrShipping` en base al `Free` cuando no exista alguna dirección de envío. Se
elija cuando el usuario es nuevo y no tiene tal dirección. Cuando suministra una dirección por primera vez, ya sea por
`checkout` o bien, el _Address Book_, el `checkout` toma la dirección nueva o elegida y actualiza el costo del envío en
el `preview`.

No se requiere que el cliente del portal elija un método dado que se considera de acuerdo al país de envío y si aplica
al algun caso adicional con respecto al peso. Por tanto, el `checkout` no muestra la vista `ShippingMethod`.