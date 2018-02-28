caso_nivelesCompletos_UnElemento = \
    {
        "categories": [
            {
                "category": "category1",
                "sub_category": [
                    {
                        "category": "HP1",
                        "sub_category": [
                            {
                                "category": "serial1",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
casoR_nivelesCompletos_UnElemento = \
    [['',"category1", "HP1", "serial1", "component1"]]

########################################################################################################################
caso_nivelesCompletos_variosElemComponentes = \
    {
        "categories": [
            {
                "category": "category1",
                "sub_category": [
                    {
                        "category": "HP1 ",
                        "sub_category": [
                            {
                                "category": "serial1",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    },
                                    {
                                        "category": "component2",
                                    },
                                    {
                                        "category": "component3",
                                    },
                                    {
                                        "category": "component4",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

casoR_nivelesCompletos_variosElementosCom = \
    [
        ['',"category1", "HP1", "serial1", "component1"]
        ,['',"category1", "HP1", "serial1", "component2"]
        ,['',"category1", "HP1", "serial1", "component3"]
        ,['',"category1", "HP1", "serial1", "component4"]
    ]
########################################################################################################################
caso_nivelesCompletos_variasCateg_UnElemComp = \
    {
        "categories": [
            {
                "category": "category1",
                "sub_category": [
                    {
                        "category": "HP1 ",
                        "sub_category": [
                            {
                                "category": "serial1",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "category": "category2",
                "sub_category": [
                    {
                        "category": "HP2",
                        "sub_category": [
                            {
                                "category": "serial2",
                                "sub_category": [
                                    {
                                        "category": "component2",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "category": "category3",
                "sub_category": [
                    {
                        "category": "HP3",
                        "sub_category": [
                            {
                                "category": "serial3",
                                "sub_category": [
                                    {
                                        "category": "component3",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

casoR_nivelesCompletos_variasCateg_UnElemComp = \
    [
        ['',"category1", "HP1", "serial1", "component1"]
        ,['',"category2", "HP2", "serial2", "component2"]
        ,['',"category3", "HP3", "serial3", "component3"]
    ]

########################################################################################################################
caso_nivelesCompletos_variasCateg_variasSerial_variosComp = \
    {
        "categories": [
            {
                "category": "category1",
                "sub_category": [
                    {
                        "category": "HP1",
                        "sub_category": [
                            {
                                "category": "serial1",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "category": "category2",
                "sub_category": [
                    {
                        "category": "HP1",
                        "sub_category": [
                            {
                                "category": "serial1",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    },
                                    {
                                        "category": "component2",
                                    },
                                    {
                                        "category": "component3",
                                    }

                                ]
                            },
                            {
                                "category": "serial2",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "category": "category3",
                "sub_category": [
                    {
                        "category": "HP1",
                        "sub_category": [
                            {
                                "category": "serial1",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    },
                                    {
                                        "category": "component2",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

casoR_nivelesCompletos_variasCateg_variasSerial_variosComp = \
    [
        ['',"category1", "HP1", "serial1", "component1"]
        , ['',"category2", "HP1", "serial1", "component1"]
        , ['',"category2", "HP1", "serial1", "component2"]
        , ['',"category2", "HP1", "serial1", "component3"]
        , ['',"category2", "HP1", "serial2", "component1"]
        , ['',"category3", "HP1", "serial1", "component1"]
        , ['',"category3", "HP1", "serial1", "component2"]
    ]
########################################################################################################################
########################################################################################################################

varios_productos_no_anidados = \
    {
        "category_url": "/parts/mercury-outboard-parts/2/0t894577-up-usa/cylinder-block",
        "image": "img/marine_engine/mercury/6970.gif",
        "products": [
            {
                "is_available": True,
                "part_number": "878-9151  2",
                "product": "878-9151 2 - Cylinder Block",
                "manufacturer": "Mercury Quicksilver",
                "diagram_number": "1",
                "replacements": []
            },
            {
                "is_available": True,
                "part_number": "22-8M0064617",
                "product": "228M0064617 - Nipple Fitting",
                "manufacturer": "Mercury Quicksilver",
                "diagram_number": "5",
                "replacements": []
            },
            {
                "is_available": True,
                "part_number": "32-812940  4",
                "product": "32-812940 4 - Hose",
                "manufacturer": "Mercury Quicksilver",
                "diagram_number": "6",
                "replacements": []
            }
        ]
    }


sin_productos = {
    "category_url": "/parts/mercury-outboard-parts/2/0t894577-up-usa/cylinder-block",
    "image": "img/marine_engine/mercury/6970.gif",
    "products": []
}

varios_productos_con_un_anidado = \
    {
        "category_url": "/parts/mercury-outboard-parts/2/0t894577-up-usa/cylinder-block",
        "image": "img/marine_engine/mercury/6970.gif",
        "products": [
            {
                "is_available": True,
                "part_number": "878-9151  2",
                "product": "878-9151 2 - Cylinder Block",
                "manufacturer": "Mercury Quicksilver",
                "diagram_number": "1",
                "replacements": [
                    {
                        "is_available": True,
                        "part_number": "22-8M0064617",
                        "product": "228M0064617 - Nipple Fitting",
                        "manufacturer": "Mercury Quicksilver",
                        "diagram_number": "5",
                        "replacements": []
                    },
                ]
            },
            {
                "is_available": True,
                "part_number": "32-812940  4",
                "product": "32-812940 4 - Hose",
                "manufacturer": "Mercury Quicksilver",
                "diagram_number": "6",
                "replacements": [
                    {
                        "is_available": True,
                        "part_number": "12-809931044",
                        "product": "12-809931044 - Washer",
                        "manufacturer": "Mercury Quicksilver",
                        "diagram_number": "10",
                        "replacements": []
                    }
                ]
            }
        ]
    }

varios_productos_anidados = \
    {
        "category_url": "/parts/mercury-outboard-parts/2/0t894577-up-usa/cylinder-block",
        "image": "img/marine_engine/mercury/6970.gif",
        "products": [
            {
                "is_available": True,
                "part_number": "878-9151  2",
                "product": "878-9151 2 - Cylinder Block",
                "manufacturer": "Mercury Quicksilver",
                "diagram_number": "1",
                "replacements": [
                    {
                        "is_available": True,
                        "part_number": "22-8M0064617",
                        "product": "228M0064617 - Nipple Fitting",
                        "manufacturer": "Mercury Quicksilver",
                        "diagram_number": "5",
                        "replacements": [
                            {
                                "is_available": True,
                                "part_number": "32-812940  4",
                                "product": "32-812940 4 - Hose",
                                "manufacturer": "Mercury Quicksilver",
                                "diagram_number": "6",
                                "replacements": [
                                    {
                                        "is_available": True,
                                        "part_number": "12-809931044",
                                        "product": "12-809931044 - Washer",
                                        "manufacturer": "Mercury Quicksilver",
                                        "diagram_number": "10",
                                        "replacements": []
                                    }
                                ]
                            }
                        ]
                    },
                ]
            },
            {
                "is_available": True,
                "part_number": "34-95304",
                "product": "34-95304 - Reed Stop, NLA",
                "manufacturer": "Mercury Quicksilver",
                "diagram_number": "12",
                "replacements": []
            }
        ]
    }


productos_repetidos_categorias = \
    {
        "category_url": "/parts/mercury-outboard-parts/2/0t894577-up-usa",
        "category_name": "serial_range",
        "category": "0T894577 & Up (USA)",
        "sub_category": [
            {
                "category_url": "/parts/mercury-outboard-parts/2/0t894577-up-usa/cylinder-block",
                "image": "img/marine_engine/mercury/6970.gif",
                "category_name": "component",
                "category": "Cylinder Block",
                "products": [
                    {
                        "is_available": True,
                        "part_number": "878-9151 2",
                        "product": "878-9151 2 - Cylinder Block",
                        "manufacturer": "Mercury Quicksilver",
                        "diagram_number": "1",
                        "replacements": [
                            {
                                "is_available": True,
                                "part_number": "22-8M0064617",
                                "product": "228M0064617 - Nipple Fitting",
                                "manufacturer": "Mercury Quicksilver",
                                "diagram_number": "5",
                                "replacements": [
                                    {
                                        "is_available": True,
                                        "part_number": "32-812940  4",
                                        "product": "32-812940 4 - Hose",
                                        "manufacturer": "Mercury Quicksilver",
                                        "diagram_number": "6",
                                        "replacements": [
                                            {
                                                "is_available": True,
                                                "part_number": "12-809931044",
                                                "product": "12-809931044 - Washer",
                                                "manufacturer": "Mercury Quicksilver",
                                                "diagram_number": "10",
                                                "replacements": []
                                            }
                                        ]
                                    }
                                ]
                            },
                        ]
                    },
                    {
                    "is_available": True,
                    "part_number": "34-95304",
                    "product": "34-95304 - Reed Stop, NLA",
                    "manufacturer": "Mercury Quicksilver",
                    "diagram_number": "12",
                    "replacements": []
                    }
                ]
            },
            {
                "category_url": "/parts/mercury-outboard-parts/2/0t894577-up-usa/cylinder-block",
                "image": "img/marine_engine/mercury/6970.gif",
                "category_name": "component",
                "category": "Cylinder Block Primera",
                "products": [
                    {
                        "is_available": True,
                        "part_number": "878-9151 2",
                        "product": "878-9151 2 - Cylinder Block",
                        "manufacturer": "Mercury Quicksilver",
                        "diagram_number": "1",
                        "replacements": []
                    },
                    {
                        "is_available": True,
                        "part_number": "34-95304",
                        "product": "34-95304 - Reed Stop, NLA",
                        "manufacturer": "Mercury Quicksilver",
                        "diagram_number": "12",
                        "replacements": [
                            {
                                "is_available": True,
                                "part_number": "22-8M0064618",
                                "product": "228M0064618 - Nipple Fitting",
                                "manufacturer": "Mercury Quicksilver",
                                "diagram_number": "5",
                                "replacements": []
                            }
                        ]
                    }
                ]
            }
        ]
    }

productos_repetidos_categorias = \
    {
        "category_url": "/parts/mercury-outboard-parts/2/0t894577-up-usa",
        "category_name": "serial_range",
        "category": "0T894577 & Up (USA)",
        "sub_category": [
            {
                "category_url": "/parts/mercury-outboard-parts/2/0t894577-up-usa/cylinder-block",
                "image": "img/marine_engine/mercury/6970.gif",
                "category_name": "component",
                "category": "Cylinder Block",
                "products": [
                    {
                        "is_available": True,
                        "part_number": "878-9151 2",
                        "product": "878-9151 2 - Cylinder Block",
                        "manufacturer": "Mercury Quicksilver",
                        "diagram_number": "1",
                        "replacements": [
                            {
                                "is_available": True,
                                "part_number": "22-8M0064617",
                                "product": "228M0064617 - Nipple Fitting",
                                "manufacturer": "Mercury Quicksilver",
                                "diagram_number": "5",
                                "replacements": [
                                    {
                                        "is_available": True,
                                        "part_number": "32-812940  4",
                                        "product": "32-812940 4 - Hose",
                                        "manufacturer": "Mercury Quicksilver",
                                        "diagram_number": "6",
                                        "replacements": [
                                            {
                                                "is_available": True,
                                                "part_number": "12-809931044",
                                                "product": "12-809931044 - Washer",
                                                "manufacturer": "Mercury Quicksilver",
                                                "diagram_number": "10",
                                                "replacements": []
                                            }
                                        ]
                                    }
                                ]
                            },
                        ]
                    },
                    {
                    "is_available": True,
                    "part_number": "34-95304",
                    "product": "34-95304 - Reed Stop, NLA",
                    "manufacturer": "Mercury Quicksilver",
                    "diagram_number": "12",
                    "replacements": []
                    }
                ]
            },
            {
                "category_url": "/parts/mercury-outboard-parts/2/0t894577-up-usa/cylinder-block",
                "image": "img/marine_engine/mercury/6970.gif",
                "category_name": "component",
                "category": "Cylinder Block Primera",
                "products": [
                    {
                        "is_available": True,
                        "part_number": "878-9151 2",
                        "product": "878-9151 2 - Cylinder Block",
                        "manufacturer": "Mercury Quicksilver",
                        "diagram_number": "1",
                        "replacements": []
                    },
                    {
                        "is_available": True,
                        "part_number": "34-95304",
                        "product": "34-95304 - Reed Stop, NLA",
                        "manufacturer": "Mercury Quicksilver",
                        "diagram_number": "12",
                        "replacements": [
                            {
                                "is_available": True,
                                "part_number": "22-8M0064618",
                                "product": "228M0064618 - Nipple Fitting",
                                "manufacturer": "Mercury Quicksilver",
                                "diagram_number": "5",
                                "replacements": []
                            }
                        ]
                    }
                ]
            }
        ]
    }