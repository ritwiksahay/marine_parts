## Ideas  de pruebas

* `updater()`
    - Excepciones: KeyError. Caso en que las cabeceras del archivo sean distintas.
    - Resultados del logger en caso de excepciones TypeError, Product.DoesNotExist, Partner.DoesNotExist, Product.MultipleObjectsReturned.
    - Contadores como resultado final

    * Pruebas de integración

* `update_by_part_number()`
    - Actualización con valores válidos de precios.
    - Creación con valores válidos de precios.
    
* `UploadFileForm` 
    - Llenado de los campos 
    
* `IndexView`
    - Comportamiento cuando `UploadFileForm` es válido e inválido.
    - Detección de errores del formulario.
    - Prueba de sistema.

* `ReviewUpdater`
    - Renderizado de la plantilla con los resultados.