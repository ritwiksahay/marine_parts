from db_handler import DBAccess
from file_handler import ExcelHandler
from django.db import transaction


def exec_excel_load(path_arch, cat, cat_base, nom_manufac, nom_origin):
    return excel_load(
        cat,
        DBAccess(cat_base),
        ExcelHandler().leer(path_arch),
        nom_manufac,
        nom_origin
    )


@transaction.atomic
def excel_load(cat, db_marine_parts, ls_prods, nom_manufac, nom_origin):
    nro = 0
    cat = db_marine_parts.crear_categoria(['', cat], None)

    for row in ls_prods:
        db_marine_parts.crear_prods(
            cat, True, row['Name'], row['SKU'], nom_manufac,
            nom_origin, '', row['Price'], row['SalePrice'], row['Cost']
        )
        nro += 1
    return nro
